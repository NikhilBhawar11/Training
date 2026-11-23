
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.records import get_by_id, load_records
from app.smart_search import smart_search

app = FastAPI(title="GadKille API")


# -----------------------------
# Request and Response Models
# -----------------------------

class ChatRequest(BaseModel):
    question: str

class AgentRequest(BaseModel):
    question: str

class GraphRequest(BaseModel):
    question: str
    thread_id: str | None = None


class GraphResumeRequest(BaseModel):
    thread_id: str
    approved: bool

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    mode: str = "Ask"
    rating: str  # "thumbs_up" or "thumbs_down"
    comment: str | None = None
    timestamp: str | None = None

class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str
    sources: list[str]


# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": "GadKille"
    }


# -----------------------------
# Fort Records
# -----------------------------

@app.get("/records")
def get_records(limit: int = 20):
    records = load_records()
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):

    record = get_by_id(record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Fort not found"
        )

    return record


# -----------------------------
# Traditional Smart Search
# -----------------------------

@app.get("/search")
def search_records(q: str):

    results = smart_search(q)

    return results


# -----------------------------
# Semantic Search
# -----------------------------


@lru_cache
def get_semantic_search():
    from app.semantic_search import SemanticSearch
    return SemanticSearch()


@lru_cache
def get_agent():
    from app.agent_loop import GadKilleAgent
    return GadKilleAgent()


@lru_cache
def get_langgraph_agent():
    from app.graph import build_graph
    return build_graph()



@app.get("/search/semantic")
def semantic_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=20)
):

    search_engine = get_semantic_search()

    results = search_engine.search(
        q,
        top_k=top_k
    )

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# -----------------------------
# RAG Pipeline
# -----------------------------

@lru_cache
def get_rag_pipeline():
    from app.rag import RAGPipeline

    return RAGPipeline(
        top_k=3,
        search_engine=get_semantic_search()
    )


@app.post("/chat", response_model=ChatResponse)
@app.post("/ask", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        rag = get_rag_pipeline()

        result = rag.answer(request.question)

        return ChatResponse(**result)

    except ValueError as error:

        raise HTTPException(
            status_code=502,
            detail=str(error)
        )


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
            "rating": feedback.rating
        }
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@app.get("/feedback")
def get_feedback(limit: int = 50):
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
def ask_question(question: str):

    return {
        "question": question,
        "message": "Question received. AI answering is handled through the RAG chat endpoint."
    }

@app.post("/agent")
def run_agent(request: AgentRequest):

    try:
        agent = get_agent()

        result = agent.run(request.question)

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@app.post("/agent/graph")
def run_langgraph_agent(request: GraphRequest):

    try:
        graph = get_langgraph_agent()

        # Generate a conversation ID if not provided
        thread_id = request.thread_id or str(uuid4())

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # Start LangGraph execution
        result = graph.invoke(
            {
                "question": request.question
            },
            config=config
        )

        # Check whether human approval is required
        if "__interrupt__" in result:

            interrupts = result["__interrupt__"]

            return {
                "status": "approval_required",
                "thread_id": thread_id,
                "approval_request": [
                    item.value
                    for item in interrupts
                    ]
            }

        return {
            "status": "completed",
            "thread_id": thread_id,
            "result": result.get("final_response")
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.post("/agent/graph/resume")
def resume_langgraph_agent(request: GraphResumeRequest):

    try:
        from langgraph.types import Command

        graph = get_langgraph_agent()

        config = {
            "configurable": {
                "thread_id": request.thread_id
            }
        }

        # Resume the interrupted workflow
        result = graph.invoke(
            Command(resume=request.approved),
            config=config
        )

        # Check if another approval is required
        if "__interrupt__" in result:
            interrupts = result["__interrupt__"]
            return {
                "status": "approval_required",
                "thread_id": request.thread_id,
                "approval_request": [
                    item.value
                    for item in interrupts
                ]
            }

        return {
            "status": "completed",
            "thread_id": request.thread_id,
            "approved": request.approved,
            "result": result.get("final_response")
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
