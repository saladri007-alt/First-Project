"""Custom CSS and HTML styling for the Shanky's Recom Streamlit application."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
}

/* Base Dark Theme Override */
.stApp {
    background-color: #131315 !important;
    color: #e5e1e4 !important;
}

/* Header & Hero Section */
.hero-container {
    background: linear-gradient(135deg, #1c1b1d 0%, #201f21 50%, #2a2a2c 100%);
    padding: 2.2rem 2rem;
    border-radius: 1.25rem;
    color: #e5e1e4;
    margin-bottom: 2rem;
    border: 1px solid rgba(233, 195, 73, 0.25);
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.65), 0 0 35px rgba(233, 195, 73, 0.08);
}

.hero-title {
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    margin-bottom: 0.5rem;
    color: #e5e1e4;
}

.hero-title .gold-text {
    color: #e9c349;
}

.hero-subtitle {
    font-size: 1rem;
    color: #e4bebc;
    max-width: 700px;
    line-height: 1.5;
}

.badge-model {
    display: inline-flex;
    align-items: center;
    background: rgba(233, 195, 73, 0.15);
    border: 1px solid rgba(233, 195, 73, 0.4);
    color: #e9c349;
    padding: 0.25rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-top: 0.75rem;
    font-family: monospace;
}

/* AI Summary Card */
.summary-box {
    background: #1c1b1d;
    border-left: 4px solid #e9c349;
    border-radius: 0.85rem;
    padding: 1.25rem 1.5rem;
    margin-bottom: 2rem;
    border-top: 1px solid rgba(255,255,255,0.05);
    border-right: 1px solid rgba(255,255,255,0.05);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.summary-title {
    font-weight: 700;
    font-size: 1.1rem;
    color: #e9c349;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
}

.summary-text {
    color: #e4bebc;
    font-size: 0.95rem;
    line-height: 1.6;
}

/* Restaurant Card Styling */
.restaurant-card {
    background: #1c1b1d;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.25s ease-in-out;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.restaurant-card:hover {
    border-color: rgba(255, 83, 90, 0.4);
    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.7), 0 0 24px rgba(255, 83, 90, 0.15);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 0.75rem;
}

.restaurant-name {
    font-size: 1.3rem;
    font-weight: 700;
    color: #e5e1e4;
    margin: 0;
}

.locality-text {
    font-size: 0.85rem;
    color: #e4bebc;
    margin-top: 0.15rem;
}

.rating-badge {
    background: rgba(233, 195, 73, 0.15);
    border: 1px solid rgba(233, 195, 73, 0.4);
    color: #e9c349;
    font-weight: 700;
    padding: 0.25rem 0.6rem;
    border-radius: 0.5rem;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.2rem;
}

.meta-row {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.85rem;
    font-size: 0.875rem;
    color: #e5e1e4;
}

.cost-pill {
    background: #2a2a2c;
    color: #e9c349;
    padding: 0.2rem 0.6rem;
    border-radius: 0.375rem;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.cuisine-text {
    color: #e4bebc;
    font-weight: 500;
}

/* AI Verdict Callout Box */
.ai-verdict-box {
    background: rgba(42, 42, 44, 0.8);
    border: 1px solid rgba(233, 195, 73, 0.3);
    border-radius: 0.75rem;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
    margin-bottom: 0.75rem;
}

.verdict-header {
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #e9c349;
    display: flex;
    align-items: center;
    gap: 0.35rem;
    margin-bottom: 0.35rem;
}

.verdict-content {
    font-size: 0.9rem;
    color: #e4bebc;
    line-height: 1.5;
    font-weight: 400;
}

/* Tags Pill Container */
.tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.75rem;
}

.tag-pill {
    background: #2a2a2c;
    color: #e5e1e4;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.55rem;
    border-radius: 0.375rem;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.tag-pill.gold {
    background: rgba(233, 195, 73, 0.15);
    color: #e9c349;
    border-color: rgba(233, 195, 73, 0.3);
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #0e0e10;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
"""


def render_restaurant_card(rec: dict) -> str:
    """Renders a single restaurant recommendation into a modern HTML card."""
    match_tags = rec.get("match_tags", [])
    tags_html = ""
    for idx, t in enumerate(match_tags):
        css_class = "tag-pill gold" if idx == 0 else "tag-pill"
        tags_html += f'<span class="{css_class}">#{t}</span>'

    cost = rec.get('estimated_cost_for_two', 600)

    return f"""
    <div class="restaurant-card">
        <div class="card-header">
            <div>
                <h3 class="restaurant-name">{rec.get('restaurant_name')}</h3>
                <div class="locality-text">📍 {rec.get('locality', 'Bangalore')}</div>
            </div>
            <div class="rating-badge">
                ★ {rec.get('rating', 4.0)}
            </div>
        </div>
        <div class="meta-row">
            <span class="cost-pill">₹{cost} for two</span>
            <span class="cuisine-text">🍽️ {rec.get('cuisine', 'Multi-Cuisine')}</span>
        </div>
        <div class="ai-verdict-box">
            <div class="verdict-header">✨ AI Dining Verdict</div>
            <div class="verdict-content">{rec.get('ai_explanation', '')}</div>
        </div>
        <div class="tag-container">
            {tags_html}
        </div>
    </div>
    """

