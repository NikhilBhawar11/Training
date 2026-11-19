"""
Shared pytest fixtures and test client for GadKille test suite.
DirectTestClient routes HTTP requests directly to FastAPI handlers,
ensuring fast, reliable tests without OS loopback socket requirements.
"""

import pytest
from fastapi import HTTPException

from app.main import (
    ChatRequest,
    FeedbackRequest,
    chat,
    get_feedback,
    get_record,
    get_records,
    health,
    save_feedback,
    search_records,
)


class MockResponse:
    """Lightweight response wrapper matching requests/httpx API."""

    def __init__(self, status_code: int, json_data):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data


class DirectTestClient:
    """Direct FastAPI test client invoking endpoints without OS sockets."""

    def get(self, url: str):
        path = url.split("?")[0]
        query_str = url.split("?")[1] if "?" in url else ""
        query_params = dict(qp.split("=") for qp in query_str.split("&") if "=" in qp)

        if path == "/health":
            return MockResponse(200, health())

        elif path == "/records":
            limit = int(query_params.get("limit", 20))
            return MockResponse(200, get_records(limit=limit))

        elif path.startswith("/records/"):
            rec_id_str = path.split("/records/")[1]
            try:
                rec_id = int(rec_id_str)
                rec = get_record(rec_id)
                return MockResponse(200, rec)
            except HTTPException as exc:
                return MockResponse(exc.status_code, {"detail": exc.detail})

        elif path == "/search":
            q = query_params.get("q", "")
            return MockResponse(200, search_records(q=q))

        elif path == "/feedback":
            limit = int(query_params.get("limit", 50))
            return MockResponse(200, get_feedback(limit=limit))

        return MockResponse(404, {"detail": "Not found"})

    def post(self, url: str, json=None):
        payload = json or {}

        if url in ("/ask", "/chat"):
            try:
                req = ChatRequest(**payload)
                resp = chat(req)
                return MockResponse(200, resp.model_dump())
            except HTTPException as exc:
                return MockResponse(exc.status_code, {"detail": exc.detail})

        elif url == "/feedback":
            try:
                req = FeedbackRequest(**payload)
                resp = save_feedback(req)
                return MockResponse(200, resp)
            except HTTPException as exc:
                return MockResponse(exc.status_code, {"detail": exc.detail})

        return MockResponse(404, {"detail": "Not found"})


@pytest.fixture(scope="session")
def client():
    """Session-scoped test client."""
    return DirectTestClient()
