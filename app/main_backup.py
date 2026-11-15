from fastapi import FastAPI, HTTPException
from app.records import load_records, get_by_id
from app.smart_search import smart_search
from pydantic import BaseModel
from pathlib import Path
import json
from functools import lru_cache
from fastapi import Query
from app.semantic_search import SemanticSearch

from app.llm import generate_response
app = FastAPI(title="GadKille API")

class ChatRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "healthy", "project": "GadKille"}


@app.get("/records")
def get_records(limit: int = 20):
    records = load_records()
    return records[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    record = get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Fort not found")

    return record

@app.post("/chat")
def chat(request: ChatRequest):

    # Load system prompt
    prompt_path = Path("prompts/system.txt")

    system_prompt = prompt_path.read_text(encoding="utf-8")

    # Generate LLM response
    response = generate_response(
        prompt=request.question,
        system_prompt=system_prompt
    )

    # Return structured JSON
    return {
        "answer": response,
        "confidence": "Not independently verified",
        "follow_up": "Would you like to know about the fort's history or trekking details?"
    }

class ChatResponse(BaseModel):
    answer: str
    confidence: str
    follow_up: str

@app.get("/search")
def search_records(q: str):
    results = smart_search(q)
    return results


@app.post("/questions")
def ask_question(question: str):
    return {
        "question": question,
        "message": "Question received. AI answering will be added later."
    }
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    BASE_DIR = Path(__file__).resolve().parent.parent

    prompt_path = BASE_DIR / "prompts" / "system.txt"

    system_prompt = prompt_path.read_text(encoding="utf-8")

    response = generate_response(
        prompt=request.question,
        system_prompt=system_prompt
    )

    try:
        result = json.loads(response)

        return ChatResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            follow_up=result["follow_up"]
        )

    except (json.JSONDecodeError, KeyError, TypeError):
        raise HTTPException(
            status_code=502,
            detail="LLM returned an invalid JSON response."
        )


@lru_cache
def get_semantic_search():
    return SemanticSearch()


@app.get("/search/semantic")
def semantic_search(
    q: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=20)
):
    search_engine = get_semantic_search()

    results = search_engine.search(q, top_k=top_k)

    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }
