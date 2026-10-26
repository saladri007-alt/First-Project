"""FastAPI routes for restaurant recommendations and dataset metadata."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status

from src.config import settings
from src.llm.client import generate_recommendations
from src.llm.schemas import RecommendationResponse, UserPreferenceInput
from src.retrieval.filter_engine import retrieve_candidates
from src.retrieval.store import store

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def health_check() -> dict[str, Any]:
    """Health check endpoint confirming API status, DB readiness, and LLM configuration."""
    stats = store.get_stats()
    return {
        "status": "healthy",
        "service": "AI Restaurant Recommendation System",
        "active_llm_provider": settings.active_llm_provider,
        "groq_model": settings.GROQ_MODEL if settings.has_groq_key else None,
        "dataset_ready": stats["total_restaurants"] > 0,
        "total_restaurants": stats["total_restaurants"],
    }


@router.get("/api/v1/metadata/cities", tags=["Metadata"])
def get_cities_and_cuisines() -> dict[str, Any]:
    """Returns available cities, popular localities, and top cuisines."""
    localities = store.get_all_localities()
    cuisines = store.get_all_cuisines()
    return {
        "cities": ["Bangalore"],
        "top_localities": localities[:25],
        "all_localities_count": len(localities),
        "top_cuisines": cuisines[:25],
        "all_cuisines_count": len(cuisines),
    }


@router.get("/api/v1/metadata/localities", tags=["Metadata"])
def get_localities() -> list[str]:
    """Returns all unique localities available in the dataset."""
    return store.get_all_localities()


@router.get("/api/v1/metadata/cuisines", tags=["Metadata"])
def get_cuisines() -> list[str]:
    """Returns all unique cuisines available in the dataset."""
    return store.get_all_cuisines()


@router.get("/api/v1/metadata/stats", tags=["Metadata"])
def get_stats() -> dict[str, Any]:
    """Returns dataset overview statistics."""
    return store.get_stats()


@router.post(
    "/api/v1/recommendations",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Recommendations"],
)
def create_recommendations(user_pref: UserPreferenceInput) -> RecommendationResponse:
    """
    Submits diner preferences and returns personalized, grounded recommendations.
    Combines fast DuckDB candidate pre-filtering with Groq LLM reasoning.
    """
    logger.info(
        f"Received recommendation request: location='{user_pref.location}', "
        f"budget='{user_pref.budget_tier}', cuisines={user_pref.cuisines}, "
        f"min_rating={user_pref.min_rating}, vibe='{user_pref.special_preferences}'"
    )

    try:
        # Step 1: Pre-filter candidate restaurants from DuckDB
        candidates, meta = retrieve_candidates(
            location=user_pref.location,
            budget_tier=user_pref.budget_tier,
            max_cost_for_two=user_pref.max_cost_for_two,
            cuisines=user_pref.cuisines,
            min_rating=user_pref.min_rating,
            special_preferences=user_pref.special_preferences,
            top_k=15,
        )

        logger.info(f"Retrieved {len(candidates)} candidates for LLM reasoning.")

        # Step 2: Invoke LLM reasoning (or graceful heuristic fallback if needed)
        response = generate_recommendations(user_pref, candidates, query_metadata=meta)
        return response

    except Exception as e:
        logger.exception("Error generating recommendations")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating recommendations: {e!s}",
        )
