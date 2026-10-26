"""Rate Limiter & Token Usage Guard for Groq API (openai/gpt-oss-120b)."""

import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Any

from src.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Tracks and enforces RPM, TPM, RPD, and TPD for Groq openai/gpt-oss-120b.
    Uses a sliding window for minute-level limits and a calendar bucket for daily limits.
    """

    def __init__(self):
        # Sliding minute window: stores (timestamp, tokens)
        self._minute_window: deque = deque()

        # Daily usage trackers
        self._current_day: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._daily_requests: int = 0
        self._daily_tokens: int = 0

    def _cleanup_old_records(self, now: float) -> None:
        """Removes entries older than 60 seconds from the sliding window."""
        cutoff = now - 60.0
        while self._minute_window and self._minute_window[0][0] < cutoff:
            self._minute_window.popleft()

        # Reset daily counters if day has rolled over
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._current_day:
            logger.info(f"Resetting daily rate limit counters for new UTC day: {today}")
            self._current_day = today
            self._daily_requests = 0
            self._daily_tokens = 0

    def can_make_request(self, estimated_tokens: int = 1000) -> tuple[bool, str]:
        """
        Pre-flight check: determines if the request can proceed without violating limits.
        Enforces safety thresholds to avoid reaching hard API limits (30 RPM, 8K TPM, 1K RPD, 200K TPD).

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        now = time.time()
        self._cleanup_old_records(now)

        # Current minute calculations
        current_minute_requests = len(self._minute_window)
        current_minute_tokens = sum(tokens for _, tokens in self._minute_window)

        # 1. Check Requests Per Minute (RPM)
        if current_minute_requests >= settings.GROQ_SAFE_RPM:
            msg = (
                f"Groq RPM limit safety guard reached ({current_minute_requests}/{settings.GROQ_RPM_LIMIT} req/min). "
                f"Falling back to heuristic engine to protect rate limits."
            )
            logger.warning(msg)
            return False, msg

        # 2. Check Tokens Per Minute (TPM)
        if current_minute_tokens + estimated_tokens > settings.GROQ_SAFE_TPM:
            msg = (
                f"Groq TPM limit safety guard reached ({current_minute_tokens + estimated_tokens}/{settings.GROQ_TPM_LIMIT} tokens/min). "
                f"Falling back to heuristic engine to protect rate limits."
            )
            logger.warning(msg)
            return False, msg

        # 3. Check Requests Per Day (RPD)
        if self._daily_requests >= settings.GROQ_SAFE_RPD:
            msg = (
                f"Groq daily requests limit safety guard reached ({self._daily_requests}/{settings.GROQ_RPD_LIMIT} req/day). "
                f"Falling back to heuristic engine."
            )
            logger.warning(msg)
            return False, msg

        # 4. Check Tokens Per Day (TPD)
        if self._daily_tokens + estimated_tokens > settings.GROQ_SAFE_TPD:
            msg = (
                f"Groq daily token limit safety guard reached ({self._daily_tokens + estimated_tokens}/{settings.GROQ_TPD_LIMIT} tokens/day). "
                f"Falling back to heuristic engine."
            )
            logger.warning(msg)
            return False, msg

        return True, "OK"

    def record_usage(self, tokens_used: int) -> None:
        """Records a completed request and its consumed tokens."""
        now = time.time()
        self._minute_window.append((now, tokens_used))
        self._daily_requests += 1
        self._daily_tokens += tokens_used

        logger.debug(
            f"Recorded Groq usage: {tokens_used} tokens. "
            f"Current Minute: {len(self._minute_window)}/{settings.GROQ_RPM_LIMIT} reqs, "
            f"{sum(t for _, t in self._minute_window)}/{settings.GROQ_TPM_LIMIT} tokens. "
            f"Daily: {self._daily_requests}/{settings.GROQ_RPD_LIMIT} reqs, "
            f"{self._daily_tokens}/{settings.GROQ_TPD_LIMIT} tokens."
        )

    def get_usage_stats(self) -> dict[str, Any]:
        """Returns real-time usage statistics and remaining capacity."""
        now = time.time()
        self._cleanup_old_records(now)

        current_rpm = len(self._minute_window)
        current_tpm = sum(t for _, t in self._minute_window)

        return {
            "current_rpm": current_rpm,
            "max_rpm": settings.GROQ_RPM_LIMIT,
            "rpm_remaining": max(0, settings.GROQ_RPM_LIMIT - current_rpm),
            "current_tpm": current_tpm,
            "max_tpm": settings.GROQ_TPM_LIMIT,
            "tpm_remaining": max(0, settings.GROQ_TPM_LIMIT - current_tpm),
            "daily_requests": self._daily_requests,
            "max_rpd": settings.GROQ_RPD_LIMIT,
            "rpd_remaining": max(0, settings.GROQ_RPD_LIMIT - self._daily_requests),
            "daily_tokens": self._daily_tokens,
            "max_tpd": settings.GROQ_TPD_LIMIT,
            "tpd_remaining": max(0, settings.GROQ_TPD_LIMIT - self._daily_tokens),
        }


# Singleton rate limiter instance
rate_limiter = RateLimiter()
