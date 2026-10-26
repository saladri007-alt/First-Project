"""Candidate Retrieval and Filter Engine: Sub-millisecond candidate generation and pruning."""

import logging
import math
import re
from typing import Any

from src.retrieval.store import store

logger = logging.getLogger(__name__)

# Common cuisine and keyword aliases for semantic mapping
CUISINE_ALIASES = {
    "pizza": "italian",
    "pasta": "italian",
    "burger": "fast food",
    "burgers": "fast food",
    "dosa": "south indian",
    "idli": "south indian",
    "biryani": "biryani",
    "dumpling": "chinese",
    "dumplings": "chinese",
    "dim sum": "chinese",
    "noodles": "chinese",
    "sushi": "japanese",
    "tacos": "mexican",
    "cocktail": "bar",
    "cocktails": "bar",
    "beer": "microbrewery",
    "brewery": "microbrewery",
    "coffee": "cafe",
    "tea": "cafe",
    "dessert": "desserts",
    "cake": "bakery",
}

# Locality aliases
LOCALITY_ALIASES = {
    "bengaluru": "bangalore",
    "koramangla": "koramangala",
    "indranagar": "indiranagar",
    "btm layout": "btm",
    "hser layout": "hsr",
    "hsr layout": "hsr",
    "white field": "whitefield",
    "jp nagar": "jp nagar",
}


def normalize_keyword(word: str) -> str:
    """Cleans punctuation and lowercases token."""
    return re.sub(r"[^\w\s]", "", word).strip().lower()


def compute_match_score(
    row: dict[str, Any],
    cuisines: list[str],
    vibe_tokens: list[str],
    max_cost: int | None = None,
) -> float:
    """
    Computes a composite relevance score for ranking candidate restaurants.
    Score components:
    - Rating score (0.35)
    - Popularity/Votes score (0.15)
    - Cuisine match overlap (0.30)
    - Special vibe / keyword match (0.20)
    """
    # 1. Rating component (0.0 to 1.0)
    rating_val = float(row.get("rating", 3.5) or 3.5)
    rating_score = max(0.0, min(1.0, (rating_val - 2.5) / 2.5))

    # 2. Popularity score based on log(votes)
    votes_val = int(row.get("votes", 0) or 0)
    popularity_score = min(1.0, math.log10(votes_val + 1) / 3.5)

    # 3. Cuisine overlap score
    raw_cuisines = row.get("cuisines_list")
    row_cuisines = []
    if raw_cuisines is not None:
        try:
            if hasattr(raw_cuisines, "tolist"):
                row_cuisines = [str(c).lower() for c in raw_cuisines.tolist()]
            elif isinstance(raw_cuisines, (list, tuple)):
                row_cuisines = [str(c).lower() for c in raw_cuisines]
            elif isinstance(raw_cuisines, str):
                row_cuisines = [c.strip().lower() for c in raw_cuisines.split(",")]
        except (ValueError, TypeError, AttributeError):
            row_cuisines = []

    if not row_cuisines and row.get("cuisines_str"):
        row_cuisines = [c.strip().lower() for c in str(row["cuisines_str"]).split(",")]

    cuisine_score = 0.5  # Neutral default if no cuisines requested
    if cuisines:
        matched = sum(
            1 for req in cuisines
            if any(req in c or c in req for c in row_cuisines)
        )
        cuisine_score = matched / max(len(cuisines), 1)

    # 4. Vibe / Keyword match
    vibe_score = 0.5  # Neutral default if no vibe requested
    if vibe_tokens:
        search_blob = str(row.get("search_text", "")).lower()
        matched_tokens = sum(1 for token in vibe_tokens if token in search_blob)
        vibe_score = min(1.0, matched_tokens / max(len(vibe_tokens), 1))

    # Composite weighted score
    final_score = (
        0.35 * rating_score +
        0.15 * popularity_score +
        0.30 * cuisine_score +
        0.20 * vibe_score
    )

    return round(final_score, 4)


def retrieve_candidates(
    location: str | None = None,
    budget_tier: str | None = None,
    max_cost_for_two: int | None = None,
    cuisines: list[str] | None = None,
    min_rating: float | None = None,
    special_preferences: str | None = None,
    top_k: int = 15,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Executes fast pre-filtering and heuristic scoring against the DuckDB store.
    Includes graceful constraint relaxation if initial constraints yield < 3 matches.

    Returns:
        Tuple of (candidates_list, metadata_dict)
    """
    conn = store.get_connection(read_only=True)
    cuisines_clean = [c.strip().lower() for c in (cuisines or []) if c.strip()]
    
    # Expand cuisine aliases
    expanded_cuisines = list(cuisines_clean)
    for c in cuisines_clean:
        if c in CUISINE_ALIASES:
            expanded_cuisines.append(CUISINE_ALIASES[c])
    expanded_cuisines = list(set(expanded_cuisines))

    # Tokenize vibe preferences
    vibe_tokens = []
    if special_preferences:
        raw_tokens = [normalize_keyword(w) for w in special_preferences.split()]
        stopwords = {"a", "an", "the", "in", "with", "and", "or", "for", "to", "at", "place", "places", "restaurant", "food"}
        vibe_tokens = [w for w in raw_tokens if len(w) > 2 and w not in stopwords]

    # Clean location
    loc_clean = None
    if location and location.strip():
        loc_str = location.strip().lower()
        loc_clean = LOCALITY_ALIASES.get(loc_str, loc_str)

    # Initial query parameters
    active_min_rating = min_rating
    active_budget_tier = budget_tier.lower() if budget_tier else None
    active_locality = loc_clean
    relaxed = False
    relaxation_notes = []

    def execute_filtered_query(loc_filter, budget_filter, rating_filter, max_cost_filter) -> list[dict[str, Any]]:
        conditions = ["1=1"]
        params = []

        if loc_filter and loc_filter not in ["bangalore", "bengaluru", "any", "all"]:
            conditions.append("(LOWER(locality) LIKE ? OR LOWER(address) LIKE ?)")
            params.extend([f"%{loc_filter}%", f"%{loc_filter}%"])

        if budget_filter and budget_filter in ["low", "medium", "high"]:
            conditions.append("budget_tier = ?")
            params.append(budget_filter)

        if max_cost_filter:
            conditions.append("cost_for_two <= ?")
            params.append(max_cost_filter)

        if rating_filter:
            conditions.append("rating >= ?")
            params.append(rating_filter)

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT * FROM restaurants
            WHERE {where_clause}
            ORDER BY votes DESC, rating DESC
            LIMIT 200
        """
        result_df = conn.execute(query, params).fetchdf()
        return result_df.to_dict(orient="records")

    # Step 1: Execute primary strict query
    records = execute_filtered_query(
        active_locality,
        active_budget_tier,
        active_min_rating,
        max_cost_for_two,
    )

    # Step 2: Constraint Relaxation Cascade (if < 3 results)
    if len(records) < 3 and (active_min_rating or active_budget_tier or active_locality):
        logger.info("Fewer than 3 candidates found. Initiating constraint relaxation cascade...")
        relaxed = True

        # Relaxation 2A: Widen budget & lower rating slightly
        if active_min_rating and active_min_rating > 3.2:
            active_min_rating = max(3.0, round(active_min_rating - 0.5, 1))
            relaxation_notes.append(f"Adjusted minimum rating to {active_min_rating}★")

        if active_budget_tier == "low":
            active_budget_tier = None  # Allow medium
            relaxation_notes.append("Expanded budget search to include mid-range venues")
        elif active_budget_tier == "high":
            active_budget_tier = None

        if max_cost_for_two:
            max_cost_for_two = int(max_cost_for_two * 1.35)
            relaxation_notes.append(f"Adjusted maximum budget to ₹{max_cost_for_two}")

        records = execute_filtered_query(
            active_locality,
            active_budget_tier,
            active_min_rating,
            max_cost_for_two,
        )

        # Relaxation 2B: Expand locality to citywide if still < 3
        if len(records) < 3 and active_locality and active_locality not in ["bangalore", "bengaluru", "any"]:
            relaxation_notes.append(f"Expanded search from '{location}' to citywide Bangalore")
            active_locality = None
            records = execute_filtered_query(
                None,
                active_budget_tier,
                active_min_rating,
                max_cost_for_two,
            )

    conn.close()

    # Step 3: Candidate Scoring and Top-K Pruning
    if not records:
        logger.warning("No records found even after constraint relaxation.")
        return [], {
            "total_candidates": 0,
            "relaxed": relaxed,
            "relaxation_notes": "; ".join(relaxation_notes),
        }

    scored_candidates = []
    for r in records:
        score = compute_match_score(r, expanded_cuisines, vibe_tokens, max_cost_for_two)
        candidate_dict = dict(r)
        candidate_dict["match_score"] = score
        scored_candidates.append(candidate_dict)

    # Sort candidates by match_score descending
    scored_candidates.sort(key=lambda x: (x["match_score"], x["votes"]), reverse=True)
    top_candidates = scored_candidates[:top_k]

    metadata = {
        "total_candidates_found": len(records),
        "selected_candidates_count": len(top_candidates),
        "relaxed": relaxed,
        "relaxation_notes": "; ".join(relaxation_notes) if relaxation_notes else "Exact constraints matched",
    }

    return top_candidates, metadata
