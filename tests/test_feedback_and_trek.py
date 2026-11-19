"""
Test 7 – Feedback endpoint (POST + GET).
Test 8 – Trek card data provider.
"""

from unittest.mock import patch

from app.trek_data import WIKIPEDIA_ATTRIBUTION, get_trek_cards_with_distance


def test_feedback_post_and_get(client, tmp_path):
    """POST /feedback stores a record; GET /feedback retrieves it."""
    tmp_file = tmp_path / "test_feedback.jsonl"

    with patch("app.main.FEEDBACK_FILE", tmp_file):
        # Post feedback
        payload = {
            "question": "Test question",
            "answer": "Test answer",
            "mode": "Ask",
            "rating": "thumbs_up",
        }
        resp = client.post("/feedback", json=payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

        # Retrieve feedback
        resp2 = client.get("/feedback")
        assert resp2.status_code == 200
        records = resp2.json()
        assert len(records) >= 1
        assert records[-1]["rating"] == "thumbs_up"


def test_trek_cards_have_required_fields():
    """Every trek card must contain the 5 mandatory fields + wikipedia_attribution."""
    cards = get_trek_cards_with_distance("Kopargaon", radius_km=100)
    assert len(cards) > 0

    required = ["height", "base_village", "time_to_climb", "water", "night_stay"]
    for card in cards:
        for field in required:
            assert field in card, f"Missing '{field}' in {card['fort_name']}"
            assert card[field], f"Empty '{field}' in {card['fort_name']}"
        assert "distance_km" in card
        assert "wikipedia_attribution" in card
        assert card["wikipedia_attribution"] == WIKIPEDIA_ATTRIBUTION


def test_trek_cards_distance_sorted():
    """Trek cards must be sorted by distance (nearest first)."""
    cards = get_trek_cards_with_distance("Pune", radius_km=200)
    for i in range(len(cards) - 1):
        assert cards[i]["distance_km"] <= cards[i + 1]["distance_km"]

