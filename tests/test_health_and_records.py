"""
Test /health endpoint and Fort records loading/retrieval.
"""


def test_health_returns_200(client):
    """GET /health must return 200 with status 'healthy' and project 'GadKille'."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "GadKille"


def test_records_returns_list(client):
    """GET /records must return a non-empty list of fort dicts."""
    response = client.get("/records")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_records_limit(client):
    """GET /records?limit=3 must return at most 3 items."""
    response = client.get("/records?limit=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


def test_record_has_required_fields(client):
    """Each fort record must contain fort_name and district."""
    response = client.get("/records?limit=1")
    data = response.json()
    fort = data[0]
    assert "fort_name" in fort
    assert "district" in fort


def test_record_by_id(client):
    """GET /records/1 must return the first fort record."""
    response = client.get("/records/1")
    assert response.status_code == 200
    data = response.json()
    assert "fort_name" in data


def test_record_by_id_not_found(client):
    """GET /records/999999 must return 404."""
    response = client.get("/records/999999")
    assert response.status_code == 404
