"""Pydantic schemas for LLM requests, candidate context, and structured responses."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class UserPreferenceInput(BaseModel):
    """User input payload capturing dining preferences and constraints."""

    location: str | None = Field(
        default="Bangalore",
        description="City or locality name (e.g., 'Indiranagar', 'Koramangala', 'Bangalore')",
    )
    budget_tier: str | None = Field(
        default=None,
        description="Budget category: 'low' (<₹400), 'medium' (₹400-₹1200), 'high' (>₹1200)",
    )
    max_cost_for_two: int | None = Field(
        default=None,
        ge=100,
        le=50000,
        description="Maximum estimated budget for two people in INR",
    )
    cuisines: list[str] | None = Field(
        default_factory=list,
        description="List of preferred cuisines (e.g., ['Italian', 'North Indian'])",
    )
    min_rating: float | None = Field(
        default=3.5,
        ge=1.0,
        le=5.0,
        description="Minimum acceptable rating on a 5.0 scale",
    )
    special_preferences: str | None = Field(
        default="",
        max_length=500,
        description="Free-form text describing vibe, occasion, dietary restrictions, or atmosphere",
    )

    @field_validator("budget_tier")
    @classmethod
    def validate_budget_tier(cls, v: str | None) -> str | None:
        if v is not None:
            v_clean = v.strip().lower()
            if v_clean in ["low", "medium", "high"]:
                return v_clean
        return None


class RestaurantCandidate(BaseModel):
    """Structured restaurant metadata passed into the LLM context."""

    restaurant_id: str
    name: str
    locality: str
    city: str = "Bangalore"
    cuisines_str: str
    rating: float
    votes: int
    cost_for_two: int
    budget_tier: str
    rest_type: str = "Casual Dining"
    dish_liked: str | None = ""
    address: str | None = ""
    url: str | None = ""


class RestaurantRecommendation(BaseModel):
    """An individual restaurant recommendation synthesized by the LLM."""

    restaurant_id: str = Field(description="Exact restaurant_id from the candidate list")
    restaurant_name: str = Field(description="Name of the restaurant")
    locality: str = Field(description="Locality / Neighborhood")
    cuisine: str = Field(description="Primary cuisine types offered")
    rating: float = Field(description="Restaurant rating (e.g., 4.3)")
    estimated_cost_for_two: int = Field(description="Estimated cost for two in INR")
    ai_explanation: str = Field(
        description="Engaging, personalized justification explaining why this spot fits user preferences, budget, and vibe"
    )
    match_tags: list[str] = Field(
        default_factory=list,
        description="2-4 short highlight tags (e.g., ['Romantic Ambiance', 'Value for Money', 'Top Rated Pasta'])",
    )


class RecommendationResponse(BaseModel):
    """Complete recommendation response payload."""

    recommendations: list[RestaurantRecommendation] = Field(
        default_factory=list,
        description="Top 3 to 5 curated dining recommendations ranked by fit",
    )
    summary: str = Field(
        description="High-level conversational overview synthesizing why these options match the user's intent"
    )
    provider_used: str = Field(default="groq", description="LLM provider or 'fallback'")
    model_used: str = Field(default="openai/gpt-oss-120b", description="Model identifier")
    is_fallback: bool = Field(default=False, description="True if generated via deterministic fallback")
    query_metadata: dict[str, Any] | None = Field(
        default=None, description="Diagnostic information, relaxation notes, and candidate counts"
    )
