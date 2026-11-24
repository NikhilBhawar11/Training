import json
import logging
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.cache import estimate_tokens, query_cache
from app.records import get_by_id, load_records
from app.smart_search import smart_search

logger = logging.getLogger("gadkille.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="GadKille API",
    description="Production-optimized REST API for Maharashtra Fort Explorer and intelligent trek advisor.",
    version="2.0.0",
)


# -----------------------------
# Middleware: Latency & Token Logging
# -----------------------------

@app.middleware("http")
async def log_latency_and_metrics_middleware(request: Request, call_next):
    """
    Measures and logs request duration, injects latency and token metrics headers.
    """
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000

    response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

    logger.info(
        f"[{request.method}] {request.url.path} - {response.status_code} in {duration_ms:.2f}ms"
    )
    return response


# -----------------------------
# Request and Response Models
# -----------------------------

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question regarding Maharashtra forts (max 1000 characters).",
    )


class AgentRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question for autonomous agent routing (max 1000 characters).",
    )


class GraphRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User question for LangGraph workflow (max 1000 characters).",
    )
    thread_id: Optional[str] = Field(
        None, max_length=100, description="Optional conversation session ID."
    )


class GraphResumeRequest(BaseModel):
    thread_id: str = Field(..., max_length=100)
    approved: bool


class FeedbackRequest(BaseModel):
    question: str = Field(..., max_length=1000)
    answer: str = Field(..., max_length=4000)
    mode: str = Field("Ask", max_length=50)
    rating: str = Field(..., pattern="^(thumbs_up|thumbs_down)$")
    comment: Optional[str] = Field(None, max_length=500)
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str
    sources: list[str]
    latency_ms: Optional[float] = None
    tokens_used: Optional[int] = None
    cached: bool = False


# -----------------------------
# Health & Status
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": "GadKille",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# -----------------------------
# Cache Metrics
# -----------------------------

@app.get("/cache/stats")
def get_cache_stats():
    """Return in-memory query cache statistics and token savings."""
    return query_cache.stats()


@app.post("/cache/clear")
def clear_cache():
    """Clear query cache."""
    query_cache.clear()
    return {"status": "success", "message": "Cache cleared successfully"}


# -----------------------------
# Fort Records
# -----------------------------

@app.get("/records")
def get_records(limit: int = Query(20, ge=1, le=250)):
    records = load_records()
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    record = get_by_id(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Fort not found")
    return record


# -----------------------------
# Traditional Smart Search (Lexical TF-IDF)
# -----------------------------

@app.get("/search")
def search_records(q: str = Query(..., min_length=1, max_length=100)):
    results = smart_search(q)
    return results


# -----------------------------
# Semantic Search (NumPy Vector Store + Gemini Embeddings)
# -----------------------------

@lru_cache
def get_semantic_search():
    from app.semantic_search import SemanticSearch

    return SemanticSearch()


@lru_cache
def get_agent():
    from app.agent_loop import GadKilleAgent

    return GadKilleAgent(rag=get_rag_pipeline())


@lru_cache
def get_langgraph_agent():
    from app.graph import build_graph

    return build_graph()


@app.get("/search/semantic")
def semantic_search(
    q: str = Query(..., min_length=1, max_length=300),
    top_k: int = Query(3, ge=1, le=20),
):
    search_engine = get_semantic_search()
    results = search_engine.search(q, top_k=top_k)
    return {
        "query": q,
        "total_results": len(results),
        "results": results,
    }


# -----------------------------
# RAG Pipeline with Cache & Token Tracking
# -----------------------------

@lru_cache
def get_rag_pipeline():
    from app.rag import RAGPipeline

    return RAGPipeline(top_k=3, search_engine=get_semantic_search())


@app.post("/chat", response_model=ChatResponse)
@app.post("/ask", response_model=ChatResponse)
def chat(request: ChatRequest):
    t_start = time.perf_counter()
    clean_q = request.question.strip()

    # 1. Check in-memory query cache for immediate sub-millisecond response
    cached_data = query_cache.get(clean_q, namespace="chat")
    if cached_data is not None:
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        resp_payload = cached_data.copy()
        resp_payload["latency_ms"] = latency_ms
        resp_payload["tokens_used"] = 0
        resp_payload["cached"] = True
        logger.info(
            f"Query served from CACHE in {latency_ms}ms (saved tokens): {clean_q[:50]}"
        )
        return ChatResponse(**resp_payload)

    # 2. Execute RAG pipeline
    try:
        rag = get_rag_pipeline()
        result = rag.answer(clean_q)

        # Estimate prompt and answer tokens
        prompt_tokens = estimate_tokens(clean_q) + 320
        answer_tokens = estimate_tokens(result.get("answer", ""))
        total_tokens = prompt_tokens + answer_tokens

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        # Cache valid responses
        if result.get("answer"):
            query_cache.set(
                clean_q, result, tokens=total_tokens, namespace="chat"
            )

        result["latency_ms"] = latency_ms
        result["tokens_used"] = total_tokens
        result["cached"] = False

        logger.info(
            f"Executed /ask RAG query in {latency_ms}ms | tokens: ~{total_tokens} | confidence: {result.get('confidence')}"
        )
        return ChatResponse(**result)

    except ValueError as error:
        raise HTTPException(status_code=502, detail=str(error))


# -----------------------------
# Feedback Endpoint
# -----------------------------

FEEDBACK_FILE = Path(__file__).resolve().parent.parent / "data" / "feedback.jsonl"


@app.post("/feedback")
def save_feedback(feedback: FeedbackRequest):
    try:
        data = feedback.model_dump()
        if not data.get("timestamp"):
            data["timestamp"] = datetime.now(timezone.utc).isoformat()

        FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

        return {
            "status": "success",
            "message": "Feedback saved successfully",
            "rating": feedback.rating,
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@app.get("/feedback")
def get_feedback(limit: int = Query(50, ge=1, le=500)):
    if not FEEDBACK_FILE.exists():
        return []

    records = []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records[-limit:]


# -----------------------------
# Questions Endpoint
# -----------------------------

@app.post("/questions")
def ask_question(question: str = Query(..., min_length=1, max_length=1000)):
    return {
        "question": question,
        "message": "Question received. AI answering is handled through the RAG chat endpoint.",
    }


# -----------------------------
# Autonomous Agent Endpoint
# -----------------------------

@app.post("/agent")
def run_agent(request: AgentRequest):
    t_start = time.perf_counter()
    try:
        agent = get_agent()
        result = agent.run(request.question)
        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        result["latency_ms"] = latency_ms
        logger.info(
            f"Executed /agent in {latency_ms}ms | action: {result.get('action')}"
        )
        return result
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


# -----------------------------
# LangGraph Agent Endpoints
# -----------------------------

@app.post("/agent/graph")
def run_langgraph_agent(request: GraphRequest):
    t_start = time.perf_counter()
    try:
        graph = get_langgraph_agent()
        thread_id = request.thread_id or str(uuid4())

        config = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke({"question": request.question}, config=config)

        latency_ms = round((time.perf_counter() - t_start) * 1000, 2)

        if "__interrupt__" in result:
            interrupts = result["__interrupt__"]
            return {
                "status": "approval_required",
                "thread_id": thread_id,
                "approval_request": [item.value for item in interrupts],
                "latency_ms": latency_ms,
            }

        return {
            "status": "completed",
            "thread_id": thread_id,
            "result": result.get("final_response"),
            "latency_ms": latency_ms,
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/agent/graph/resume")
def resume_langgraph_agent(request: GraphResumeRequest):
    try:
        from langgraph.types import Command

        graph = get_langgraph_agent()
        config = {"configurable": {"thread_id": request.thread_id}}

        result = graph.invoke(Command(resume=request.approved), config=config)

        if "__interrupt__" in result:
            interrupts = result["__interrupt__"]
            return {
                "status": "approval_required",
                "thread_id": request.thread_id,
                "approval_request": [item.value for item in interrupts],
            }

        return {
            "status": "completed",
            "thread_id": request.thread_id,
            "approved": request.approved,
            "result": result.get("final_response"),
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
