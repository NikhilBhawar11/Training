"""
Test 3 – Smart search (TF-IDF) returns ranked results.
"""

from app.smart_search import smart_search


def test_smart_search_returns_results():
    """smart_search('Nashik') should return forts with a relevance_score."""
    results = smart_search("Nashik")
    assert isinstance(results, list)
    assert len(results) > 0
    # Every hit must carry a relevance_score > 0
    for fort in results:
        assert "relevance_score" in fort
        assert fort["relevance_score"] > 0


def test_smart_search_empty_query():
    """An empty query should return an empty list."""
    results = smart_search("")
    assert results == []


def test_search_endpoint(client):
    """GET /search?q=Pune must return 200 with a list."""
    response = client.get("/search?q=Pune")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

