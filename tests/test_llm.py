"""Unit tests for LLM schemas, prompt builders, grounding guardrails, and fallbacks."""

from src.config import settings
from src.llm.client import (
    clean_json_text,
    generate_heuristic_fallback,
    generate_recommendations,
)
from src.llm.prompts import build_recommendation_prompt
from src.llm.schemas import (
    RecommendationResponse,
    RestaurantRecommendation,
    UserPreferenceInput,
)


def test_user_preference_schema_valid():
    user_input = UserPreferenceInput(
        location="Indiranagar",
        budget_tier="medium",
        max_cost_for_two=1000,
        cuisines=["Italian", "Chinese"],
        min_rating=4.0,
        special_preferences="Quiet date night with wine",
    )
    assert user_input.location == "Indiranagar"
    assert user_input.budget_tier == "medium"
    assert user_input.min_rating == 4.0
    assert "Italian" in user_input.cuisines


def test_user_preference_budget_validation():
    # Invalid budget tier resets to None
    user_input = UserPreferenceInput(budget_tier="super_expensive")
    assert user_input.budget_tier is None


def test_clean_json_text():
    raw_markdown = "```json\n{\"recommendations\": []}\n```"
    assert clean_json_text(raw_markdown) == "{\"recommendations\": []}"

    raw_plain = "  {\"status\": \"ok\"}  "
    assert clean_json_text(raw_plain) == "{\"status\": \"ok\"}"


def test_build_prompt_structure():
    user_input = UserPreferenceInput(
        location="Bangalore",
        cuisines=["Italian"],
        min_rating=4.2,
        special_preferences="Outdoor seating",
    )
    mock_candidates = [
        {
            "restaurant_id": "ZOM_00001",
            "name": "Toscano",
            "locality": "UB City",
            "cuisines_str": "Italian",
            "rating": 4.5,
            "votes": 1200,
            "cost_for_two": 1500,
            "budget_tier": "high",
            "rest_type": "Casual Dining",
            "dish_liked": "Pizza, Wine",
        }
    ]

    prompt = build_recommendation_prompt(user_input, mock_candidates)
    assert "Italian" in prompt
    assert "ZOM_00001" in prompt
    assert "Toscano" in prompt
    assert "[CANDIDATES]" in prompt


def test_heuristic_fallback_generation():
    user_input = UserPreferenceInput(location="Koramangala", budget_tier="low")
    mock_candidates = [
        {
            "restaurant_id": "ZOM_00010",
            "name": "Corner House",
            "locality": "Koramangala",
            "cuisines_str": "Desserts, Ice Cream",
            "rating": 4.6,
            "votes": 3500,
            "cost_for_two": 300,
            "budget_tier": "low",
            "rest_type": "Dessert Parlor",
        }
    ]

    response = generate_heuristic_fallback(user_input, mock_candidates, reason="Test fallback")
    assert response.is_fallback is True
    assert response.provider_used == "fallback"
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant_id == "ZOM_00010"
    assert response.recommendations[0].restaurant_name == "Corner House"
    assert "4.6★" in response.recommendations[0].ai_explanation


def test_grounding_guardrail_suppresses_hallucinations(monkeypatch):
    user_input = UserPreferenceInput(location="Indiranagar")
    mock_candidates = [
        {
            "restaurant_id": "ZOM_00001",
            "name": "Toit",
            "locality": "Indiranagar",
            "cuisines_str": "Microbrewery, Italian",
            "rating": 4.7,
            "votes": 5000,
            "cost_for_two": 1500,
            "budget_tier": "high",
        }
    ]

    # Mock response returning one valid ID and one hallucinated ID
    mock_response = RecommendationResponse(
        recommendations=[
            RestaurantRecommendation(
                restaurant_id="ZOM_00001",
                restaurant_name="Toit",
                locality="Indiranagar",
                cuisine="Microbrewery",
                rating=4.7,
                estimated_cost_for_two=1500,
                ai_explanation="Great craft beer",
            ),
            RestaurantRecommendation(
                restaurant_id="ZOM_FAKE_9999",  # Hallucinated ID
                restaurant_name="NonExistent Bistro",
                locality="Indiranagar",
                cuisine="French",
                rating=4.9,
                estimated_cost_for_two=2000,
                ai_explanation="Fake restaurant explanation",
            ),
        ],
        summary="Top picks",
        provider_used="groq",
    )

    # Patch call_groq_llm to return mock_response
    monkeypatch.setattr("src.llm.client.call_groq_llm", lambda pref, cands: mock_response)
    monkeypatch.setattr(type(settings), "active_llm_provider", property(lambda self: "groq"))

    response = generate_recommendations(user_input, mock_candidates)

    # Verify that the hallucinated ID was suppressed by the grounding check
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant_id == "ZOM_00001"
    assert response.recommendations[0].restaurant_name == "Toit"
