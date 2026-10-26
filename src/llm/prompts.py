"""Token-optimized prompt templates and grounding instructions for LLM dining recommendation."""

import json
from typing import Any

from src.config import settings
from src.llm.schemas import UserPreferenceInput

SYSTEM_PROMPT = """You are DineWise, a premier AI dining concierge inspired by Zomato.
Your task is to analyze candidate restaurants and select the TOP 6 best recommendations satisfying user constraints.

CRITICAL GROUNDING RULES:
1. ZERO HALLUCINATION: Only select from the provided [CANDIDATES] list. Do NOT invent venues.
2. PRESERVE IDs: Use the exact `restaurant_id` from candidates.
3. TAILORED REASONING: Provide a concise, engaging `ai_explanation` (2 sentences) explaining why this fits their vibe, budget, and cravings.
4. STRICT JSON: Output valid JSON adhering exactly to the requested schema. No markdown outside JSON.
"""


def format_candidates_for_prompt(candidates: list[dict[str, Any]]) -> str:
    """
    Serializes top candidate list into a compact, token-efficient JSON string.
    Limits candidates to MAX_CANDIDATES_FOR_LLM (default 6) and truncates verbose text.
    """
    top_cands = candidates[: settings.MAX_CANDIDATES_FOR_LLM]
    lean_candidates = []

    for c in top_cands:
        # Compact dishes to top 2 items
        dishes = c.get("dish_liked") or ""
        short_dishes = ", ".join([d.strip() for d in dishes.split(",")[:2]]) if dishes else "House Specials"

        lean_candidates.append(
            {
                "id": c.get("restaurant_id"),
                "name": c.get("name"),
                "locality": c.get("locality"),
                "cuisine": c.get("cuisines_str"),
                "rating": c.get("rating"),
                "votes": c.get("votes"),
                "cost": c.get("cost_for_two"),
                "budget": c.get("budget_tier"),
                "dishes": short_dishes,
            }
        )

    # Compact JSON without extra indentation to conserve tokens
    return json.dumps(lean_candidates, separators=(",", ":"))


def build_recommendation_prompt(
    user_pref: UserPreferenceInput,
    candidates: list[dict[str, Any]],
) -> str:
    """
    Constructs a compact, high-density prompt to keep token usage strictly below 8K TPM.
    """
    candidates_json = format_candidates_for_prompt(candidates)
    cuisines_str = ", ".join(user_pref.cuisines) if user_pref.cuisines else "Any"
    budget_desc = user_pref.budget_tier or "Any"
    if user_pref.max_cost_for_two:
        budget_desc += f" (max ₹{user_pref.max_cost_for_two})"

    prompt = f"""[PREFERENCES]
Location: {user_pref.location or 'Bangalore'} | Cuisines: {cuisines_str} | Budget: {budget_desc} | Min Rating: {user_pref.min_rating or 3.5}★ | Vibe/Occasion: {user_pref.special_preferences or 'General dining'}

[CANDIDATES]
{candidates_json}

[OUTPUT SCHEMA]
Return JSON:
{{
  "recommendations": [
    {{
      "restaurant_id": "<id_from_candidates>",
      "restaurant_name": "<name>",
      "locality": "<locality>",
      "cuisine": "<cuisine>",
      "rating": <float>,
      "estimated_cost_for_two": <int>,
      "ai_explanation": "<Concise 2-sentence justification matching vibe and budget>",
      "match_tags": ["<tag1>", "<tag2>", "<tag3>"]
    }}
  ],
  "summary": "<2-sentence summary highlighting top picks for this diner>"
}}"""
    return prompt
