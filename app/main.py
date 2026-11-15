
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.records import load_records, get_by_id
from app.smart_search import smart_search
from app.semantic_search import SemanticSearch
from app.rag import RAGPipeline


app = FastAPI(title="GadKille API")


# -----------------------------
# Request and Response Models
# -----------------------------

class ChatRequest(BaseModel):
    question: str


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
    return SemanticSearch()


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
    return RAGPipeline(top_k=3)


@app.post("/chat", response_model=ChatResponse)
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
# Questions Endpoint
# -----------------------------

@app.post("/questions")
def ask_question(question: str):

    return {
        "question": question,
        "message": "Question received. AI answering is handled through the RAG chat endpoint."
    }
