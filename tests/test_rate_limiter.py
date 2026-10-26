"""Unit tests for Groq rate limiter, token guards, and response caching."""

from src.config import settings
from src.llm.cache import RecommendationCache
from src.llm.rate_limiter import RateLimiter
from src.llm.schemas import (
    RecommendationResponse,
    RestaurantRecommendation,
    UserPreferenceInput,
)


def test_rate_limiter_allows_initial_request():
    limiter = RateLimiter()
    can_proceed, reason = limiter.can_make_request(estimated_tokens=500)
    assert can_proceed is True
    assert reason == "OK"


def test_rate_limiter_blocks_on_high_rpm():
    limiter = RateLimiter()
    # Simulate filling the minute window to safe RPM limit
    for _ in range(settings.GROQ_SAFE_RPM):
        limiter.record_usage(tokens_used=100)

    # Next request should be blocked
    can_proceed, reason = limiter.can_make_request(estimated_tokens=500)
    assert can_proceed is False
    assert "Groq RPM limit safety guard reached" in reason


def test_rate_limiter_blocks_on_high_tpm():
    limiter = RateLimiter()
    # Simulate a single heavy request that consumes safe TPM limit
    limiter.record_usage(tokens_used=settings.GROQ_SAFE_TPM)

    # Next request requiring tokens should be blocked
    can_proceed, reason = limiter.can_make_request(estimated_tokens=500)
    assert can_proceed is False
    assert "Groq TPM limit safety guard reached" in reason


def test_recommendation_cache_set_and_get():
    cache = RecommendationCache(ttl_seconds=60)
    user_pref = UserPreferenceInput(
        location="Indiranagar",
        cuisines=["Italian"],
        budget_tier="medium",
        min_rating=4.0,
    )

    mock_rec = RecommendationResponse(
        recommendations=[
            RestaurantRecommendation(
                restaurant_id="ZOM_00001",
                restaurant_name="Toit",
                locality="Indiranagar",
                cuisine="Italian",
                rating=4.7,
                estimated_cost_for_two=1500,
                ai_explanation="Top brewpub with pizza",
            )
        ],
        summary="Top pick",
        provider_used="groq",
    )

    # Cache should be initially empty
    assert cache.get(user_pref) is None

    # Store in cache
    cache.set(user_pref, mock_rec)

    # Retrieve from cache
    cached = cache.get(user_pref)
    assert cached is not None
    assert cached.recommendations[0].restaurant_name == "Toit"
    assert cache.size == 1


def test_recommendation_cache_expiration():
    # Cache with 0 second TTL expires immediately
    cache = RecommendationCache(ttl_seconds=-1)
    user_pref = UserPreferenceInput(location="Koramangala")
    mock_rec = RecommendationResponse(
        recommendations=[], summary="empty", provider_used="groq"
    )

    cache.set(user_pref, mock_rec)
    # Should be expired
    assert cache.get(user_pref) is None
