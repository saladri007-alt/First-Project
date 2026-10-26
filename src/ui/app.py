"""DineWise AI: AI-Powered Restaurant Recommendation Dashboard (Streamlit)."""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st

from src.config import settings
from src.llm.cache import recommendation_cache
from src.llm.client import generate_recommendations
from src.llm.rate_limiter import rate_limiter
from src.llm.schemas import UserPreferenceInput
from src.retrieval.filter_engine import retrieve_candidates
from src.retrieval.store import store
from src.ui.styles import CUSTOM_CSS, render_restaurant_card

# Page configuration
st.set_page_config(
    page_title="Shanky's Recom | Intelligent Dining Discovery",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_metadata():
    """Caches metadata for fast UI rendering."""
    localities = store.get_all_localities()
    cuisines = store.get_all_cuisines()
    stats = store.get_stats()
    return localities, cuisines, stats


localities, all_cuisines, stats = load_metadata()

# Hero Header
model_badge_text = (
    f"⚡ Shanky's Recom Engine • Groq ({settings.GROQ_MODEL})"
    if settings.has_groq_key
    else "🛡️ Shanky's Recom Engine (Deterministic Mode)"
)

st.markdown(
    f"""
    <div class="hero-container">
        <div class="hero-title">Shanky's <span class="gold-text">Recom</span> ✨</div>
        <div class="hero-subtitle">
            Curating Exceptional Culinary Evenings Tailored to Your Vibe.
            Sub-second semantic discovery powered by DuckDB pre-filtering and Groq (openai/gpt-oss-120b) reasoning.
        </div>
        <div class="badge-model">{model_badge_text}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "search_executed" not in st.session_state:
    st.session_state.search_executed = False
if "current_response" not in st.session_state:
    st.session_state.current_response = None
if "current_meta" not in st.session_state:
    st.session_state.current_meta = None
if "vibe_input_text" not in st.session_state:
    st.session_state.vibe_input_text = ""


# Preset quick-click buttons
st.write("#### 🎯 Quick Curated Presets")
col_p1, col_p2, col_p3, col_p4 = st.columns(4)

with col_p1:
    if st.button("🍷 Romantic Date Night", use_container_width=True):
        st.session_state.selected_locality = "Indiranagar"
        st.session_state.selected_cuisines = ["Italian", "Continental"]
        st.session_state.selected_budget = "Mid-Range (₹400 - ₹1200)"
        st.session_state.vibe_input_text = "Cozy romantic ambiance, candle light date with pasta and wine"

with col_p2:
    if st.button("☕ Cozy Work Cafe", use_container_width=True):
        st.session_state.selected_locality = "Koramangala"
        st.session_state.selected_cuisines = ["Cafe", "Desserts"]
        st.session_state.selected_budget = "Mid-Range (₹400 - ₹1200)"
        st.session_state.vibe_input_text = "Quiet work-friendly cafe with great coffee and Wi-Fi"

with col_p3:
    if st.button("🍻 Craft Beer & Rooftop", use_container_width=True):
        st.session_state.selected_locality = "Indiranagar"
        st.session_state.selected_cuisines = ["Continental", "Finger Food"]
        st.session_state.selected_budget = "Fine Dining (> ₹1200)"
        st.session_state.vibe_input_text = "Open-air rooftop microbrewery with live music and fresh craft beer"

with col_p4:
    if st.button("🥟 Budget Street Treats", use_container_width=True):
        st.session_state.selected_locality = "BTM"
        st.session_state.selected_cuisines = ["Chinese", "Fast Food", "South Indian"]
        st.session_state.selected_budget = "Budget (< ₹400)"
        st.session_state.vibe_input_text = "Delicious quick bites under budget with great flavors"

st.markdown("<br>", unsafe_allow_html=True)


# --- SIDEBAR SEARCH CONTROLS ---
with st.sidebar:
    st.markdown("### 🔍 Dining Preferences")

    # Locality dropdown
    locality_options = ["All Bangalore Localities"] + localities
    default_loc_idx = 0
    if hasattr(st.session_state, "selected_locality") and st.session_state.selected_locality in localities:
        default_loc_idx = locality_options.index(st.session_state.selected_locality)

    selected_loc = st.selectbox(
        "Locality / Area:",
        options=locality_options,
        index=default_loc_idx,
        help="Select a neighborhood in Bangalore or search citywide",
    )

    # Cuisine Multi-select
    popular_cuisines = [
        "North Indian",
        "Italian",
        "Chinese",
        "South Indian",
        "Cafe",
        "Continental",
        "Biryani",
        "Desserts",
        "Fast Food",
        "Asian",
        "Beverages",
    ]
    default_cuisines = []
    if hasattr(st.session_state, "selected_cuisines"):
        default_cuisines = [c for c in st.session_state.selected_cuisines if c in all_cuisines]

    selected_cuisines = st.multiselect(
        "Preferred Cuisines:",
        options=all_cuisines,
        default=default_cuisines,
        help="Select one or more cuisines",
    )

    # Budget Selection
    budget_map = {
        "All Budgets": None,
        "Budget (< ₹400)": "low",
        "Mid-Range (₹400 - ₹1200)": "medium",
        "Fine Dining (> ₹1200)": "high",
    }
    budget_labels = list(budget_map.keys())
    default_budget_idx = 0
    if hasattr(st.session_state, "selected_budget") and st.session_state.selected_budget in budget_labels:
        default_budget_idx = budget_labels.index(st.session_state.selected_budget)

    selected_budget_label = st.radio(
        "Budget Tier:",
        options=budget_labels,
        index=default_budget_idx,
    )
    budget_tier_val = budget_map[selected_budget_label]

    # Minimum Rating Slider
    min_rating_val = st.slider(
        "Minimum Rating:",
        min_value=3.0,
        max_value=4.8,
        value=3.8,
        step=0.1,
        format="★ %.1f",
    )

    # Free-form Vibe & Ambiance input
    vibe_text = st.text_area(
        "Atmosphere / Special Occasion:",
        value=st.session_state.vibe_input_text,
        placeholder="e.g. Pet-friendly outdoor seating, anniversary dinner, quiet reading spot",
        help="Describe what you feel like experiencing",
    )

    # Search Button
    search_clicked = st.button("🚀 Find Matching Restaurants", type="primary", use_container_width=True)

    # Rate Limiter & Diagnostics Monitor
    st.markdown("---")
    st.markdown("#### ⚡ System & Rate Limits")
    limiter_stats = rate_limiter.get_usage_stats()
    col_rpm, col_tpm = st.columns(2)
    with col_rpm:
        st.metric("RPM Capacity", f"{limiter_stats['rpm_remaining']}/{limiter_stats['max_rpm']}")
    with col_tpm:
        st.metric("TPM Capacity", f"{limiter_stats['tpm_remaining']:,}")

    col_cache, col_db = st.columns(2)
    with col_cache:
        st.metric("Memory Cache", f"{recommendation_cache.size} queries")
    with col_db:
        st.metric("Database", f"{stats['total_restaurants']:,} spots")


# --- RECOMMENDATION LOGIC ---
if search_clicked:
    loc_param = None if selected_loc == "All Bangalore Localities" else selected_loc
    user_pref = UserPreferenceInput(
        location=loc_param or "Bangalore",
        budget_tier=budget_tier_val,
        cuisines=selected_cuisines,
        min_rating=min_rating_val,
        special_preferences=vibe_text,
    )

    with st.spinner("🤖 Discovering candidate spots and generating AI dining insights..."):
        # 1. Retrieve candidates
        candidates, meta = retrieve_candidates(
            location=user_pref.location,
            budget_tier=user_pref.budget_tier,
            cuisines=user_pref.cuisines,
            min_rating=user_pref.min_rating,
            special_preferences=user_pref.special_preferences,
            top_k=settings.MAX_CANDIDATES_FOR_LLM,
        )

        # 2. Invoke recommendation reasoning
        response = generate_recommendations(user_pref, candidates, query_metadata=meta)
        st.session_state.current_response = response
        st.session_state.current_meta = meta
        st.session_state.search_executed = True


# --- RESULTS DISPLAY ---
if st.session_state.search_executed and st.session_state.current_response:
    response = st.session_state.current_response
    meta = st.session_state.current_meta

    # Relaxation Notification Banner if applicable
    if meta and meta.get("relaxed"):
        st.markdown(
            f"""
            <div class="relaxation-banner">
                ℹ️ <strong>Search Adjustment:</strong> {meta.get('relaxation_notes')}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Provider & Model Source Badge
    provider_icon = "⚡" if response.provider_used == "groq" else ("💾" if response.provider_used == "cache" else "🛡️")
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <h3 style="margin:0; color:#1E293B;">Top Curated Recommendations</h3>
            <span style="font-size:0.85rem; color:#64748B; background:#F1F5F9; padding:0.25rem 0.6rem; border-radius:0.375rem;">
                {provider_icon} Source: <strong>{response.provider_used.upper()}</strong> ({response.model_used})
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Conversational Summary
    st.markdown(
        f"""
        <div class="summary-box">
            <div class="summary-title">📝 Culinary Concierge Overview</div>
            <div class="summary-text">{response.summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Restaurant Cards
    if response.recommendations:
        # Display in 2-column responsive layout
        for i in range(0, len(response.recommendations), 2):
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown(
                    render_restaurant_card(response.recommendations[i].model_dump()),
                    unsafe_allow_html=True,
                )
            if i + 1 < len(response.recommendations):
                with col_right:
                    st.markdown(
                        render_restaurant_card(response.recommendations[i + 1].model_dump()),
                        unsafe_allow_html=True,
                    )
    else:
        st.warning("No recommendations could be generated for the specified criteria.")

elif not st.session_state.search_executed:
    # Initial landing guide
    st.info("👈 Use the sidebar filters to customize your location, budget, and cravings, or click any of the preset cards above!")
