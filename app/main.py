from fastapi import FastAPI, HTTPException
from app.records import load_records, get_by_id
from app.smart_search import smart_search

app = FastAPI(title="GadKille API")


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