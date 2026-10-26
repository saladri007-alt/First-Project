# Epicure AI: AI-Powered Restaurant Recommendation System

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg)
![DuckDB](https://img.shields.io/badge/DuckDB-0.10%2B-FFF000.svg)
![Groq](https://img.shields.io/badge/Groq-openai%2Fgpt--oss--120b-F55036.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)
![Pytest](https://img.shields.io/badge/Tests-41%20Passed-brightgreen.svg)

An enterprise-grade, ultra-low-latency AI dining concierge combining high-speed columnar filtering with large language model reasoning (`openai/gpt-oss-120b` on Groq). Features strict candidate grounding, proactive 4-tier rate limit defense, zero-downtime deterministic fallback, and dual interfaces (an obsidian luxury web application and an analytical Streamlit dashboard).

---

## 🌟 Key Architecture & Highlights

1. **Sub-Millisecond Candidate Retrieval (DuckDB & Parquet)**:
   - Queries 12,000+ cleaned Zomato restaurant records in $< 50\text{ms}$.
   - Evaluates multi-attribute match scores combining rating, cuisine overlap, locality proximity, and semantic vibe.
   - Intelligent constraint relaxation cascade automatically widens bounds when queries are over-constrained.

2. **Grounded LLM Reasoning via Groq (`openai/gpt-oss-120b`)**:
   - Zero-hallucination guarantee: Verifies every recommended venue against candidates using `restaurant_id` validation.
   - Tailored dining verdict explaining *why* the venue fits the user's specific budget, vibe, and cuisine preferences.
   - Enforces strict Pydantic JSON schemas.

3. **Multi-Pillar Rate Limit & Quota Resilience**:
   - Explicitly configured for `openai/gpt-oss-120b` quotas:
     - **30 RPM** (Requests Per Minute)
     - **8,000 TPM** (Tokens Per Minute)
     - **1,000 RPD** (Requests Per Day)
     - **200,000 TPD** (Tokens Per Day)
   - **Pre-flight Sliding Window Limiter**: Pre-emptively inspects consumption and diverts traffic safely before HTTP 429 occurs.
   - **In-Memory TTL Query Cache**: Reuses responses for identical searches at 0 token cost and 0 latency.
   - **Deterministic Heuristic Fallback**: Zero-downtime guarantee; immediately serves rule-based recommendations if the LLM is unreachable or quotas are saturated.

4. **Dual Presentation Layers**:
   - **Epicure AI Luxury Web App**: High-end dark glassmorphic design (`#131315`, gold `#e9c349`, crimson `#ff535a`) served directly at `/` by FastAPI. Includes interactive VIP priority booking modals, atmospheric tag matrix, and live filters.
   - **Streamlit Analytical Dashboard**: Interactive playground for querying, inspecting metadata distributions, and adjusting search parameters.

---

## 🏗️ System Architecture

```
User Request (Web UI / Streamlit / REST API)
                    │
                    ▼
          [ FastAPI Endpoint ]
                    │
                    ▼
     [ Candidate Retrieval Engine ] ─── queries ───► [ DuckDB / Parquet ]
    (Locality, Budget, Cuisines, Vibe)                (12,000+ records)
                    │
           Candidates Pruned (Top 15)
                    │
                    ▼
     [ Rate Limiter & Response Cache ]
    (30 RPM / 8K TPM / 1K RPD / 200K TPD)
       ├── Hit? ──► Return Cached Result (0ms)
       │
       └── Miss ──► Safe to Proceed?
                    ├── No (Near Quota) ──► [ Heuristic Fallback Engine ]
                    │
                    └── Yes (Within Bounds)
                              │
                              ▼
                     [ Groq LLM API ]
                  (openai/gpt-oss-120b)
                              │
                              ▼
                   [ Grounding Guardrail ]
               (Suppress Hallucinated IDs)
                              │
                              ▼
               [ Verified Recommendations ]
```

---

## 📁 Project Directory Structure

```
NextLeap_Proj/
├── data/
│   ├── raw/                       # Cached raw dataset snapshots
│   └── processed/
│       └── restaurants.parquet    # Cleaned, indexed Parquet dataset
├── Docs/
│   ├── architecture.md            # System architecture blueprint
│   ├── implementation-plan.md     # 7-phase detailed delivery plan
│   ├── problemStatement.md        # Core requirements & metrics
│   ├── edge-case.md               # Edge case mitigation matrix
│   └── eval.md                    # Evaluation & benchmarking framework
├── src/
│   ├── config.py                  # Pydantic v2 application configuration
│   ├── api/
│   │   ├── main.py                # FastAPI entry point & static mounting
│   │   └── routes.py              # API routes & endpoint controllers
│   ├── data/
│   │   ├── ingest.py              # Dataset streamer from Hugging Face
│   │   └── preprocessor.py        # Data sanitization & feature engineering
│   ├── llm/
│   │   ├── cache.py               # In-memory query cache
│   │   ├── client.py              # Groq client & fallback orchestrator
│   │   ├── prompts.py             # Grounded prompt templates
│   │   ├── rate_limiter.py        # Sliding-window token & request limiter
│   │   └── schemas.py             # Pydantic validation schemas
│   ├── retrieval/
│   │   ├── filter_engine.py       # Candidate retrieval & scoring
│   │   └── store.py               # DuckDB connection & query manager
│   └── ui/
│       ├── app.py                 # Streamlit application
│       ├── styles.py              # CSS design tokens & card styling
│       └── static/                # Luxury Web Frontend assets & HTML
│           ├── index.html         # Epicure AI Dynamic Web App
│           └── images/            # Curated ambient restaurant photography
├── tests/
│   ├── test_api.py                # FastAPI endpoint integration tests
│   ├── test_config.py             # Configuration tests
│   ├── test_e2e.py                # End-to-end verification (TC-01 to TC-07)
│   ├── test_filter.py             # Candidate filter & latency tests
│   ├── test_llm.py                # LLM prompting & grounding tests
│   ├── test_preprocessor.py       # Data sanitization unit tests
│   ├── test_rate_limiter.py       # Rate limiter window tests
│   └── test_ui.py                 # Streamlit UI tests
├── .env.example                   # Environment configuration template
├── README.md                      # Project documentation
└── requirements.txt               # Pinned Python dependencies
```

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- Git

### 2. Environment Configuration
Clone the repository and set up a Python virtual environment:

```bash
git clone <repo-url>
cd NextLeap_Proj

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. API Keys Configuration
Create a `.env` file in the project root:

```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
LOG_LEVEL=INFO
```

> **Note**: If `GROQ_API_KEY` is omitted or empty, the application automatically operates in deterministic heuristic fallback mode, ensuring 100% operational uptime without crashes.

---

## 🖥️ Running the Application

### Option A: Launch the Web App & FastAPI Backend
Starts the FastAPI service with the luxury **Epicure AI** web interface served directly at the root URL:

```bash
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Epicure AI Web Frontend**: Open `http://127.0.0.1:8000/` in your browser.
- **Interactive Swagger Docs**: Open `http://127.0.0.1:8000/docs`.
- **Health Check**: `http://127.0.0.1:8000/health`.

### Option B: Launch the Streamlit Dashboard
```bash
streamlit run src/ui/app.py
```
Opens the interactive Streamlit analytics concierge at `http://localhost:8501`.

---

## 📡 API Reference

### 1. Health Status
`GET /health`
```json
{
  "status": "healthy",
  "service": "AI Restaurant Recommendation System",
  "active_llm_provider": "groq",
  "groq_model": "openai/gpt-oss-120b",
  "dataset_ready": true,
  "total_restaurants": 12499
}
```

### 2. Cities & Top Metadata
`GET /api/v1/metadata/cities`
```json
{
  "cities": ["Bangalore"],
  "top_localities": ["Indiranagar", "Koramangala", "Whitefield", ...],
  "top_cuisines": ["North Indian", "Italian", "Chinese", ...]
}
```

### 3. Generate Recommendations
`POST /api/v1/recommendations`

**Request Body:**
```json
{
  "location": "Indiranagar",
  "budget_tier": "medium",
  "cuisines": ["Italian"],
  "min_rating": 4.0,
  "special_preferences": "Authentic woodfired pizza with cozy outdoor seating"
}
```

**Response Body:**
```json
{
  "recommendations": [
    {
      "restaurant_id": "ZOM_00142",
      "restaurant_name": "Toscano",
      "locality": "Indiranagar",
      "cuisine": "Italian, Pizza",
      "rating": 4.5,
      "estimated_cost_for_two": 1500,
      "ai_explanation": "Toscano is the quintessential Italian dining venue in Indiranagar, renowned for artisanal sourdough pizza and handcrafted pasta.",
      "match_tags": ["Medium", "4.5★ Rating", "Casual Dining"]
    }
  ],
  "summary": "Selected top Italian dining matches in Indiranagar featuring authentic woodfired pizza.",
  "provider_used": "groq",
  "model_used": "openai/gpt-oss-120b",
  "is_fallback": false,
  "query_metadata": {
    "total_matched": 42,
    "selected_candidates_count": 10,
    "relaxed": false
  }
}
```

---

## 🧪 Automated Testing

The project has comprehensive test coverage spanning all architectural layers:

```bash
# Run all unit, integration, and E2E tests
pytest -v

# Run only End-to-End verification scenarios
pytest tests/test_e2e.py -v

# Run Candidate Retrieval benchmarks
pytest tests/test_filter.py -v
```

### Test Coverage Summary:
- `tests/test_api.py`: FastAPI endpoints, status codes, payload validation.
- `tests/test_filter.py`: DuckDB filtering, candidate ranking, relaxation cascade, sub-50ms latency benchmark.
- `tests/test_llm.py`: Schema validation, prompt formatting, hallucination guardrails, fallback generators.
- `tests/test_preprocessor.py`: Rating extraction, price sanitization, budget categorization.
- `tests/test_rate_limiter.py`: Sliding window limits, token usage recording, proactive bounds enforcement.
- `tests/test_ui.py`: Streamlit component rendering and CSS styling tokens.
- `tests/test_e2e.py`: Complete lifecycle verification covering all 7 E2E scenarios (TC-01 through TC-07).

---

## 🛡️ Edge Case & Error Handling Matrix

| Scenario | System Behavior |
| :--- | :--- |
| **Over-constrained query (0 matches)** | Constraint Relaxation Cascade progressively broadens budget and locality; returns nearest top matches with user notification. |
| **Groq 429 Rate Limit / Quota Saturation** | Pre-flight rate limiter diverts to Heuristic Fallback engine; serves rule-based recommendations without user delay. |
| **Groq Network Timeout / Outage** | Automatically falls back to deterministic rule-based ranking engine. Zero 500 errors returned to users. |
| **LLM Hallucinates a Fake Venue** | Grounding Guardrail cross-references all returned `restaurant_id`s against candidate pool; suppresses non-existent IDs. |
| **Prompt Injection Attempts** | User input is sanitized and placed in isolated `<user_query>` XML blocks; persona integrity is preserved. |

---

## 📜 License
MIT License. Built for the NextLeap AI Product Engineering Track.
