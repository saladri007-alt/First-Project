"""FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router
from src.config import settings
from src.retrieval.store import store

logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle event handler for database verification on startup."""
    logger.info("Initializing AI Restaurant Recommendation API...")
    stats = store.get_stats()
    logger.info(
        f"Database initialized: {stats['total_restaurants']:,} restaurants loaded. "
        f"Active LLM provider: {settings.active_llm_provider}"
    )
    yield
    logger.info("Shutting down AI Restaurant Recommendation API.")


app = FastAPI(
    title="AI-Powered Restaurant Recommendation API",
    description=(
        "Production-grade intelligent dining discovery API inspired by Zomato. "
        "Combines sub-millisecond DuckDB pre-filtering with Groq (openai/gpt-oss-120b) "
        "to deliver personalized, human-like restaurant recommendations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

from pathlib import Path

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static web assets (Epicure AI UI)
static_dir = Path(__file__).parent.parent / "ui" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(str(static_dir / "index.html"))

# Include all API routes
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
