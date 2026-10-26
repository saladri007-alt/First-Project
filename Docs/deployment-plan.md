# Production Deployment Plan: Shanky's Recom on Railway & Vercel

This document outlines the step-by-step production deployment strategy for **Shanky's Recom (AI Restaurant Recommendation System)**, separating concerns between:
1. **Backend Engine on Railway**: High-performance FastAPI server running Uvicorn, DuckDB analytical pre-filtering, and Groq (`openai/gpt-oss-120b`) LLM synthesis with rate limiting and fallback protection.
2. **Frontend UI on Vercel**: Ultra-fast global Edge CDN hosting the latest refined dining dark-mode interface (`src/ui/static/`), routing API requests transparently to Railway.

---

## Architecture Overview

```
                                      ┌─────────────────────────────────────────────────────────┐
                                      │                   END USER BROWSER                      │
                                      └────────────────────────────┬────────────────────────────┘
                                                                   │
                                                HTTPS Requests     │
                                                                   ▼
                                      ┌─────────────────────────────────────────────────────────┐
                                      │                   VERCEL EDGE NETWORK                   │
                                      │            (https://shankys-recom.vercel.app)           │
                                      │                                                         │
                                      │  • Static Assets (HTML5, Tailwind CDN, Custom CSS, SVG) │
                                      │  • Global Edge Caching (Cache-Control headers)          │
                                      │  • Reverse Proxy (/api/* -> Railway Backend)           │
                                      └────────────────────────────┬────────────────────────────┘
                                                                   │
                                                Reverse Proxy      │
                                                /api/v1/*          │
                                                                   ▼
                                      ┌─────────────────────────────────────────────────────────┐
                                      │                   RAILWAY CLUSTER                       │
                                      │      (https://<your-project>.up.railway.app)            │
                                      │                                                         │
                                      │  • Uvicorn ASGI Server on $PORT (0.0.0.0)               │
                                      │  • FastAPI REST Engine (/api/v1/recommendations)        │
                                      │  • DuckDB Analytical Engine (12,157 Venue Records)      │
                                      │  • In-Memory Response Cache (1-Hour TTL)                │
                                      │  • Groq Rate Limiter Guard (30 RPM / 8K TPM)            │
                                      └────────────────────────────┬────────────────────────────┘
                                                                   │
                                                                   │ Groq API Call
                                                                   ▼
                                      ┌─────────────────────────────────────────────────────────┐
                                      │                   GROQ CLOUD INFERENCE                  │
                                      │              Model: openai/gpt-oss-120b                 │
                                      └─────────────────────────────────────────────────────────┘
```

---

## Deployment Matrix

| Component | Target Platform | Source Directory | Configuration File | Public Domain Example |
| :--- | :--- | :--- | :--- | :--- |
| **Backend API & Engine** | **Railway** | Repository Root (`./`) | [`railway.json`](../railway.json), [`Procfile`](../Procfile) | `https://first-project-production.up.railway.app` |
| **Frontend Web UI** | **Vercel** | Repository Root (`./`) | [`vercel.json`](../vercel.json) | `https://first-project.vercel.app` |
| **Unified Alternative** | **Railway** | Repository Root (`./`) | Serves both API and Web UI on `/` | `https://first-project-production.up.railway.app` |

---

## Pre-Requisites

1. **GitHub Repository**: [https://github.com/saladri007-alt/First-Project.git](https://github.com/saladri007-alt/First-Project.git) (Synced to branch `main`).
2. **Railway Account**: Free account at [railway.app](https://railway.app).
3. **Vercel Account**: Free account at [vercel.com](https://vercel.com).
4. **Groq API Key**: Active key from [console.groq.com](https://console.groq.com/keys).

---

## Phase 1: Deploy Backend to Railway

Railway runs Python 3.12 containers with automatic port detection, zero-downtime rollouts, and persistent memory.

### Step 1.1: Create New Project on Railway
1. Open the [Railway Dashboard](https://railway.app/dashboard).
2. Click **"+ New Project"**.
3. Choose **"Deploy from GitHub repo"**.
4. Select `saladri007-alt/First-Project` (give GitHub permissions if prompted).

### Step 1.2: Configure Environment Variables
Inside the newly created service on Railway:
1. Click on the service -> Navigate to the **Variables** tab.
2. Click **"New Variable"** (or **"Raw Editor"**) and add the following:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=openai/gpt-oss-120b
   DEFAULT_LLM_PROVIDER=groq
   APP_ENV=production
   LOG_LEVEL=INFO
   ```
   *(Note: Railway automatically injects `PORT`. Our [`railway.json`](../railway.json) binds `uvicorn` to `0.0.0.0:${PORT:-8000}`)*.

### Step 1.3: Generate Public HTTPS Domain
1. In the service dashboard, navigate to the **Settings** tab.
2. Scroll to the **Networking** section.
3. Click **"Generate Domain"** (e.g., `first-project-production.up.railway.app`).
4. Copy this public URL.

### Step 1.4: Verify Backend Health
Once deployed (indicated by a green checkmark):
1. Test Health Endpoint:
   ```bash
   curl -I https://<your-railway-domain>/health
   # Expected: HTTP/2 200 OK -> {"status":"healthy", "database_connected":true}
   ```
2. Test Swagger UI:
   Open `https://<your-railway-domain>/docs` in your browser.
3. Test Recommendations API:
   ```bash
   curl -X POST https://<your-railway-domain>/api/v1/recommendations \
     -H "Content-Type: application/json" \
     -d '{"location":"Indiranagar","budget_tier":"high","min_rating":4.2,"special_preferences":"Romantic rooftop dinner"}'
   ```

---

## Phase 2: Deploy Frontend to Vercel

Vercel provides edge caching, automatic SSL, and instant global CDN delivery for your frontend.

### Step 2.1: Update Backend Destination in `vercel.json`
Open [`vercel.json`](../vercel.json) in your project and replace `YOUR-RAILWAY-APP.up.railway.app` with your actual Railway domain from Phase 1:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "cleanUrls": true,
  "rewrites": [
    {
      "source": "/api/:match*",
      "destination": "https://<your-railway-domain>/api/:match*"
    },
    {
      "source": "/static/:match*",
      "destination": "/src/ui/static/:match*"
    },
    {
      "source": "/(.*)",
      "destination": "/src/ui/static/index.html"
    }
  ],
  "headers": [
    {
      "source": "/static/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

Commit and push this change:
```bash
git add vercel.json
git commit -m "Configure Vercel API rewrite to Railway backend"
git push origin main
```

### Step 2.2: Import Project on Vercel
1. Log into [vercel.com](https://vercel.com).
2. Click **"Add New..."** -> **"Project"**.
3. Locate `saladri007-alt/First-Project` and click **"Import"**.
4. Configure Project Settings:
   * **Framework Preset**: `Other`
   * **Root Directory**: `./` (Default root)
   * **Build Command**: *(leave blank)*
   * **Output Directory**: *(leave blank)*
5. Click **"Deploy"**.

### Step 2.3: Verify Vercel Deployment
1. Vercel will complete deployment in ~15 seconds and assign a URL (e.g., `https://first-project-xxx.vercel.app`).
2. Open the URL on your phone or laptop.
3. Test that:
   - The hero title says **"Orchestrating Taste, Atmosphere, and Moment"**.
   - Filters display **"Destination & Quarter"**, **"Investment Tier"**, **"Gastronomic Benchmark"**, and **"Flavor Profile"**.
   - Clicking **"Synthesize Matches"** generates **6 curated restaurant cards**.
   - Network inspector confirms `/api/v1/recommendations` is proxied cleanly with `HTTP 200 OK` (no CORS warnings).

---

## Phase 3: Dual Deployment Mode (Alternative Single-Service Option)

Your Railway deployment is **already fully capable of serving both the frontend and backend simultaneously**:
- The FastAPI application automatically mounts `src/ui/static` and serves `index.html` at the root path (`/`).
- Therefore, your Railway domain (`https://<your-railway-domain>/`) can function as a standalone, all-in-one web app without requiring Vercel if you prefer single-service simplicity.
- Using Vercel alongside Railway provides superior edge caching, lower TTFB (Time to First Byte) for HTML/images, and independent frontend scaling.

---

## Phase 4: Post-Deployment Smoke Tests & Verification

Execute the following test matrix to confirm production readiness:

| Test Case | Method | Expected Result | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **TC-01: Health & DB** | `GET /health` | Database connected, 12,157 venues | HTTP 200, status="healthy" |
| **TC-02: Metadata Endpoints** | `GET /api/v1/metadata/localities` | List of Bangalore localities | Array length > 80 |
| **TC-03: Multi-Restaurant Recommendation** | `POST /api/v1/recommendations` | 6 curated restaurant cards | `recommendations.length == 6` |
| **TC-04: Vercel Asset Proxy** | `GET /static/images/logo.png` | PNG asset delivered via Vercel CDN | HTTP 200, image/png |
| **TC-05: Fallback Guarantee** | Disconnect Groq API key | Heuristic engine serves results | `is_fallback: true`, HTTP 200 |

---

## Phase 5: CI/CD & Maintenance Workflows

1. **Continuous Deployment (Auto-Redeploy)**:
   - Both Railway and Vercel automatically listen to the `main` branch.
   - Any `git push origin main` triggers an automatic build and rolling update with zero downtime.
2. **Rotating API Keys**:
   - To update your `GROQ_API_KEY`, simply change it in the Railway Variables dashboard. Railway will automatically restart the process in 5 seconds.
3. **Database Updates**:
   - If new restaurant datasets are compiled, run `python src/data/preprocessor.py`, commit `data/processed/zomato.duckdb`, and push to GitHub. Railway will automatically reload the updated DuckDB database.
