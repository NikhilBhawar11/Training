"""
Test /ask endpoint and RAG pipeline with a fake LLM.
"""

import json
from unittest.mock import MagicMock, patch

from app.rag import RAGPipeline

FAKE_LLM_RESPONSE = json.dumps({
    "answer": "Harishchandragad is a fort in Ahmednagar district [Source 1].",
    "confidence": "high",
    "follow_up": "Would you like trek details?"
})

MOCK_CHUNKS = [
    {
        "text": "Harishchandragad is a hill fort located in Ahmednagar district.",
        "score": 0.85,
        "metadata": {
            "title": "Harishchandragad",
            "source": "https://en.wikipedia.org/wiki/Harishchandragad"
        }
    }
]


def test_ask_endpoint_with_fake_llm(client):
    """POST /ask must return a valid ChatResponse when RAG is answered with fake data."""
    mock_rag = MagicMock()
    mock_rag.answer.return_value = {
        "answer": "Harishchandragad is a fort in Ahmednagar district [Source 1].",
        "confidence": "high",
        "follow_up": "Would you like trek details?",
        "sources": ["https://en.wikipedia.org/wiki/Harishchandragad"]
    }

    with patch("app.main.get_rag_pipeline", return_value=mock_rag):
        response = client.post("/ask", json={"question": "Tell me about Harishchandragad"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "Harishchandragad" in data["answer"]
    assert data["confidence"] == "high"
    assert data["sources"] == ["https://en.wikipedia.org/wiki/Harishchandragad"]
    assert "follow_up" in data


def test_chat_alias_works(client):
    """POST /chat is an alias for /ask and should return the expected response."""
    mock_rag = MagicMock()
    mock_rag.answer.return_value = {
        "answer": "Sinhagad is situated near Pune [Source 1].",
        "confidence": "medium",
        "follow_up": "Need directions?",
        "sources": ["https://en.wikipedia.org/wiki/Sinhagad"]
    }

    with patch("app.main.get_rag_pipeline", return_value=mock_rag):
        response = client.post("/chat", json={"question": "Height of Sinhagad?"})

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "Sinhagad" in data["answer"]


def test_rag_pipeline_answer_with_fake_llm():
    """RAGPipeline.answer() directly using fake LLM response and mocked retrieval."""
    with patch("app.rag.SemanticSearch") as MockSearchClass, \
         patch("app.rag.generate_response", return_value=FAKE_LLM_RESPONSE):

        mock_search_instance = MockSearchClass.return_value
        mock_search_instance.search.return_value = MOCK_CHUNKS

        rag = RAGPipeline()
        result = rag.answer("Tell me about Harishchandragad")

        assert result["confidence"] == "high"
        assert "[Source 1]" in result["answer"]
        assert "https://en.wikipedia.org/wiki/Harishchandragad" in result["sources"]


def test_rag_pipeline_empty_context():
    """RAGPipeline handles irrelevant/missing context gracefully."""
    with patch("app.rag.SemanticSearch") as MockSearchClass:
        mock_search_instance = MockSearchClass.return_value
        # No relevant chunks retrieved
        mock_search_instance.search.return_value = []

        rag = RAGPipeline()
        result = rag.answer("Unknown fort in outer space")

        assert result["answer"] == "I don't know"
        assert result["confidence"] == "low"
        assert result["sources"] == []
