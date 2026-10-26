"""In-memory TTL response cache to save tokens and request limits."""

import hashlib
import json
import logging
import time
from typing import Any

from src.config import settings
from src.llm.schemas import RecommendationResponse, UserPreferenceInput

logger = logging.getLogger(__name__)


class RecommendationCache:
    """Caches recommendations in memory by query hash to prevent redundant LLM calls."""

    def __init__(self, ttl_seconds: int | None = None):
        self.ttl = ttl_seconds or settings.CACHE_TTL_SECONDS
        self._cache: dict[str, dict[str, Any]] = {}

    def _generate_key(self, user_pref: UserPreferenceInput) -> str:
        """Generates a deterministic hash key representing user dining preferences."""
        normalized_data = {
            "location": (user_pref.location or "").strip().lower(),
            "budget_tier": (user_pref.budget_tier or "").strip().lower(),
            "max_cost_for_two": user_pref.max_cost_for_two,
            "min_rating": round(user_pref.min_rating or 3.5, 1),
            "cuisines": sorted([c.strip().lower() for c in (user_pref.cuisines or [])]),
            "special_preferences": (user_pref.special_preferences or "").strip().lower(),
        }
        serialized = json.dumps(normalized_data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get(self, user_pref: UserPreferenceInput) -> RecommendationResponse | None:
        """Retrieves cached response if present and not expired."""
        key = self._generate_key(user_pref)
        entry = self._cache.get(key)
        if not entry:
            return None

        # Check TTL
        if time.time() - entry["timestamp"] > self.ttl:
            del self._cache[key]
            return None

        logger.info("Cache Hit: Retrieved recommendations from memory cache (0 tokens used).")
        cached_response: RecommendationResponse = entry["response"]
        return cached_response

    def set(self, user_pref: UserPreferenceInput, response: RecommendationResponse) -> None:
        """Stores response in cache with current timestamp."""
        key = self._generate_key(user_pref)
        self._cache[key] = {
            "response": response,
            "timestamp": time.time(),
        }

    def clear(self) -> None:
        """Clears all cached responses."""
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


# Singleton cache instance
recommendation_cache = RecommendationCache()
