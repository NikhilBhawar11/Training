"""
Test Agent tool: forts_within_km distance calculator and haversine_distance.
"""

import pytest

from app.tools import forts_within_km, haversine_distance


def test_forts_within_km_kopargaon():
    """forts_within_km('Kopargaon', 50) should return Ankai Fort (~34 km)."""
    results = forts_within_km("Kopargaon", 50)
    assert isinstance(results, list)
    assert len(results) >= 1
    names = [f["fort_name"] for f in results]
    assert "Ankai Fort" in names


def test_forts_within_km_sorted_by_distance():
    """Results must be sorted nearest-first."""
    results = forts_within_km("Kopargaon", 150)
    for i in range(len(results) - 1):
        assert results[i]["distance_km"] <= results[i + 1]["distance_km"]


def test_forts_within_km_unknown_town():
    """An unknown town must raise ValueError."""
    with pytest.raises(ValueError, match="Town not found"):
        forts_within_km("Atlantis", 100)


def test_haversine_zero_distance():
    """Same coordinates must yield 0.0 km."""
    assert haversine_distance(19.0, 73.0, 19.0, 73.0) == 0.0


def test_haversine_known_pair():
    """Geodesic distance between Kopargaon and Pune is ~164.8 km."""
    dist = haversine_distance(19.8823, 74.4760, 18.5204, 73.8567)
    assert 150 < dist < 180
