import sys
sys.stdout.reconfigure(encoding='utf-8')

from src.config import settings
from src.retrieval.filter_engine import retrieve_candidates
from src.llm.schemas import UserPreferenceInput
from src.llm.client import generate_recommendations

print("Testing End-to-End Recommendation with Groq:")
print(f"  Active Provider: {settings.active_llm_provider}")
print(f"  Model: {settings.GROQ_MODEL}")

user_pref = UserPreferenceInput(
    location="Indiranagar",
    cuisines=["Italian"],
    budget_tier="medium",
    min_rating=4.0,
    special_preferences="Cozy romantic date night with pasta and nice ambiance",
)

print(f"\n1. Retrieving candidates for: {user_pref.location} ({user_pref.cuisines})...")
candidates, meta = retrieve_candidates(
    location=user_pref.location,
    cuisines=user_pref.cuisines,
    budget_tier=user_pref.budget_tier,
    min_rating=user_pref.min_rating,
    special_preferences=user_pref.special_preferences,
    top_k=10,
)
print(f"   Found {len(candidates)} candidates. (DuckDB search: {meta['relaxation_notes']})")

print("\n2. Calling Groq LLM (openai/gpt-oss-120b) to synthesize recommendations...")
response = generate_recommendations(user_pref, candidates, query_metadata=meta)

print(f"\n3. Recommendation Results (Provider: {response.provider_used}, Model: {response.model_used}, Fallback: {response.is_fallback}):")
print(f"Summary: {response.summary}\n")
for i, rec in enumerate(response.recommendations, 1):
    print(f"[{i}] {rec.restaurant_name} ({rec.locality}) - {rec.rating} stars | Rs. {rec.estimated_cost_for_two} for two")
    print(f"    Cuisine: {rec.cuisine}")
    print(f"    Tags: {rec.match_tags}")
    print(f"    AI Verdict: {rec.ai_explanation}\n")
