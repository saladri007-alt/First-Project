"""Unit tests and benchmarks for candidate retrieval and filter engine."""

import time

from src.retrieval.filter_engine import retrieve_candidates
from src.retrieval.store import store


def test_store_metadata_methods():
    localities = store.get_all_localities()
    assert len(localities) > 10
    assert "Indiranagar" in localities or "Koramangala" in localities

    cuisines = store.get_all_cuisines()
    assert len(cuisines) > 10
    assert "North Indian" in cuisines or "Italian" in cuisines

    stats = store.get_stats()
    assert stats["total_restaurants"] > 10000
    assert stats["average_rating"] > 3.0
    assert stats["average_cost_for_two"] > 0


def test_retrieve_candidates_standard():
    candidates, meta = retrieve_candidates(
        location="Indiranagar",
        budget_tier="medium",
        min_rating=4.0,
        top_k=10,
    )
    assert len(candidates) > 0
    assert len(candidates) <= 10
    assert meta["selected_candidates_count"] == len(candidates)

    for c in candidates:
        assert c["rating"] >= 4.0
        assert "indiranagar" in c["locality"].lower() or "indiranagar" in c["address"].lower()
        assert "restaurant_id" in c
        assert "name" in c
        assert "match_score" in c


def test_retrieve_candidates_cuisine_ranking():
    candidates, _ = retrieve_candidates(
        location="Koramangala",
        cuisines=["Italian", "Pizza"],
        min_rating=3.8,
        top_k=5,
    )
    assert len(candidates) > 0
    top_pick = candidates[0]
    # Verify top pick has relevant cuisine
    assert "italian" in str(top_pick["cuisines_str"]).lower() or "pizza" in str(top_pick["cuisines_str"]).lower() or "cafe" in str(top_pick["rest_type"]).lower()


def test_retrieve_candidates_relaxation_cascade():
    # Intentionally over-constrained query to trigger relaxation
    candidates, meta = retrieve_candidates(
        location="Mysore Road",
        budget_tier="high",
        min_rating=4.8,
        top_k=5,
    )
    assert len(candidates) > 0
    assert meta["relaxed"] is True
    assert "relaxation_notes" in meta


def test_retrieval_latency_benchmark():
    # Benchmark query latency on 12,000+ records
    start_time = time.perf_counter()
    candidates, _ = retrieve_candidates(
        location="Bangalore",
        budget_tier="medium",
        cuisines=["Chinese", "Thai"],
        min_rating=3.9,
        special_preferences="cozy outdoor rooftop with music",
        top_k=15,
    )
    duration_ms = (time.perf_counter() - start_time) * 1000.0

    assert len(candidates) > 0
    # Latency exit criteria: Sub-50ms (giving 100ms tolerance for initial disk load in CI)
    assert duration_ms < 100.0, f"Retrieval latency was too high: {duration_ms:.2f}ms"
