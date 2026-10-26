"""Unit tests for UI helper functions and HTML card rendering."""

from src.ui.styles import render_restaurant_card


def test_render_restaurant_card_contains_fields():
    mock_rec = {
        "restaurant_id": "ZOM_00001",
        "restaurant_name": "Toscano",
        "locality": "UB City",
        "cuisine": "Italian, Mediterranean",
        "rating": 4.5,
        "estimated_cost_for_two": 1500,
        "ai_explanation": "Perfect romantic courtyard ambiance with acclaimed wine pairings.",
        "match_tags": ["Romantic", "Outdoor Seating", "Italian"],
    }

    card_html = render_restaurant_card(mock_rec)

    assert "Toscano" in card_html
    assert "UB City" in card_html
    assert "4.5" in card_html
    assert "1500" in card_html
    assert "AI Dining Verdict" in card_html
    assert "Perfect romantic courtyard ambiance" in card_html
    assert "#Romantic" in card_html
    assert "#Italian" in card_html


def test_render_restaurant_card_handles_defaults():
    empty_rec = {}
    card_html = render_restaurant_card(empty_rec)
    assert "restaurant-card" in card_html
    assert "AI Dining Verdict" in card_html
