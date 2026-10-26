"""LLM Client and Orchestration Layer: Groq integration with rate limit guards, caching, and fallback."""

import json
import logging
from typing import Any

from src.config import settings
from src.llm.cache import recommendation_cache
from src.llm.prompts import SYSTEM_PROMPT, build_recommendation_prompt
from src.llm.rate_limiter import rate_limiter
from src.llm.schemas import (
    RecommendationResponse,
    RestaurantRecommendation,
    UserPreferenceInput,
)

logger = logging.getLogger(__name__)


def clean_json_text(text: str) -> str:
    """Strips markdown code blocks and trims whitespace around JSON responses."""
    text_clean = text.strip()
    if text_clean.startswith("```json"):
        text_clean = text_clean[7:]
    elif text_clean.startswith("```"):
        text_clean = text_clean[3:]
    text_clean = text_clean.removesuffix("```")
    return text_clean.strip()


def generate_heuristic_fallback(
    user_pref: UserPreferenceInput,
    candidates: list[dict[str, Any]],
    reason: str = "Fallback mode active",
    query_metadata: dict[str, Any] | None = None,
) -> RecommendationResponse:
    """
    Generates rule-based deterministic recommendations when LLM rate limits are saturated
    or when API keys are unconfigured, guaranteeing zero user-facing downtime.
    """
    logger.info(f"Serving recommendations via heuristic fallback engine. Reason: {reason}")
    top_candidates = candidates[:6] if candidates else []

    recommendations: list[RestaurantRecommendation] = []
    for c in top_candidates:
        cuisines_str = c.get("cuisines_str") or ", ".join(c.get("cuisines_list", ["Multi-cuisine"]))
        locality = c.get("locality", "Bangalore")
        rating = float(c.get("rating", 4.0))
        cost = int(c.get("cost_for_two", 500))
        name = c.get("name", "Popular Dining Spot")
        res_id = c.get("restaurant_id", "ZOM_00000")

        explanation = (
            f"Recommended because it is a highly rated venue ({rating}★) in {locality} "
            f"specializing in {cuisines_str}. It provides solid value for your {c.get('budget_tier', 'medium')} "
            f"budget at approximately ₹{cost} for two."
        )

        tags = [c.get("budget_tier", "medium").title(), f"{rating}★ Rating"]
        if c.get("rest_type"):
            tags.append(str(c["rest_type"]).split(",")[0].strip())

        recommendations.append(
            RestaurantRecommendation(
                restaurant_id=res_id,
                restaurant_name=name,
                locality=locality,
                cuisine=cuisines_str,
                rating=rating,
                estimated_cost_for_two=cost,
                ai_explanation=explanation,
                match_tags=tags[:3],
            )
        )

    summary_text = (
        f"Selected top {len(recommendations)} dining matches in {user_pref.location or 'Bangalore'}. "
        f"({reason})"
    )

    return RecommendationResponse(
        recommendations=recommendations,
        summary=summary_text,
        provider_used="fallback",
        model_used="rule-based-heuristic",
        is_fallback=True,
        query_metadata=query_metadata,
    )


def call_groq_llm(
    user_pref: UserPreferenceInput,
    candidates: list[dict[str, Any]],
) -> RecommendationResponse:
    """
    Calls Groq API using model openai/gpt-oss-120b with strict token bounds and rate limit recording.
    """
    from groq import Groq, RateLimitError

    client = Groq(api_key=settings.GROQ_API_KEY)
    user_prompt = build_recommendation_prompt(user_pref, candidates)

    logger.info(
        f"Dispatching prompt to Groq (Model: {settings.GROQ_MODEL}, Max Tokens: {settings.MAX_COMPLETION_TOKENS})..."
    )

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=settings.MAX_COMPLETION_TOKENS,
            response_format={"type": "json_object"},
            timeout=20.0,
        )

        # Track token consumption in rate limiter
        total_tokens = getattr(getattr(completion, "usage", None), "total_tokens", 850)
        rate_limiter.record_usage(total_tokens)

        raw_response = completion.choices[0].message.content or ""
        clean_json = clean_json_text(raw_response)
        data = json.loads(clean_json)

        # Validate against schema
        recs = [RestaurantRecommendation(**r) for r in data.get("recommendations", [])]
        summary = data.get("summary", "Top dining recommendations curated for your request.")

        return RecommendationResponse(
            recommendations=recs,
            summary=summary,
            provider_used="groq",
            model_used=settings.GROQ_MODEL,
            is_fallback=False,
        )

    except RateLimitError as rle:
        logger.error(f"Groq 429 RateLimitError encountered: {rle}")
        raise
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        raise


def generate_recommendations(
    user_pref: UserPreferenceInput,
    candidates: list[dict[str, Any]],
    query_metadata: dict[str, Any] | None = None,
) -> RecommendationResponse:
    """
    Main recommendation orchestrator with:
    1. Response Caching (0 token cost on repeated queries)
    2. Pre-flight Rate Limit Guard (respects 30 RPM, 8K TPM, 1K RPD, 200K TPD)
    3. LLM Synthesis via Groq (openai/gpt-oss-120b)
    4. Hallucination suppression via Grounding Guardrail
    5. Graceful Heuristic Fallback
    """
    if not candidates:
        return RecommendationResponse(
            recommendations=[],
            summary="No candidates found matching your criteria.",
            provider_used="none",
            model_used="none",
            is_fallback=True,
            query_metadata=query_metadata,
        )

    # 1. Check in-memory cache
    cached_response = recommendation_cache.get(user_pref)
    if cached_response is not None:
        return cached_response

    candidate_ids = {c["restaurant_id"]: c for c in candidates}
    active_provider = settings.active_llm_provider
    response: RecommendationResponse | None = None

    # 2. Check Rate Limits before calling LLM
    can_proceed, limit_reason = rate_limiter.can_make_request(estimated_tokens=1000)

    if not can_proceed:
        # Pre-emptively fallback to heuristic engine to protect rate limit bounds
        return generate_heuristic_fallback(
            user_pref, candidates, reason=limit_reason, query_metadata=query_metadata
        )

    # 3. Invoke LLM Provider
    if active_provider == "groq":
        try:
            response = call_groq_llm(user_pref, candidates)
        except Exception as e:  # noqa: BLE001 - Resilient fallback for any upstream failure
            logger.warning(f"Groq call failed, falling back to heuristic engine: {e}")
            response = None

    # 4. Fallback execution if LLM fails or is unconfigured
    if response is None:
        response = generate_heuristic_fallback(
            user_pref,
            candidates,
            reason="Heuristic fallback active (protecting rate limits or handling API response)",
            query_metadata=query_metadata,
        )
    else:
        response.query_metadata = query_metadata

    # 5. Grounding & Hallucination Guardrail Check
    verified_recs = []
    for rec in response.recommendations:
        if rec.restaurant_id in candidate_ids:
            verified_recs.append(rec)
        else:
            logger.warning(
                f"Grounding Guard: Suppressed hallucinated restaurant ID '{rec.restaurant_id}' ({rec.restaurant_name})"
            )

    if not verified_recs:
        return generate_heuristic_fallback(
            user_pref, candidates, reason="All LLM outputs failed grounding verification", query_metadata=query_metadata
        )

    response.recommendations = verified_recs

    # 6. Store valid response in cache (only cache real LLM responses to optimize future queries)
    if not response.is_fallback:
        recommendation_cache.set(user_pref, response)

    return response
