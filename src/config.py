"""Global configuration and environment settings."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Base Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env if present
ENV_PATH = PROJECT_ROOT / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


class Settings:
    """Application configuration settings."""

    # Application
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # LLM Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    DEFAULT_LLM_PROVIDER: str = os.getenv("DEFAULT_LLM_PROVIDER", "groq").lower()

    # Groq openai/gpt-oss-120b Rate Limits & Guardrails
    # Official limits: 30 RPM, 1K RPD, 8K TPM, 200K TPD
    GROQ_RPM_LIMIT: int = 30
    GROQ_SAFE_RPM: int = 25  # Safety threshold to prevent hitting 30 RPM
    GROQ_TPM_LIMIT: int = 8000
    GROQ_SAFE_TPM: int = 6500  # Safety threshold to prevent exceeding 8K TPM
    GROQ_RPD_LIMIT: int = 1000
    GROQ_SAFE_RPD: int = 950  # Daily request safety limit
    GROQ_TPD_LIMIT: int = 200000
    GROQ_SAFE_TPD: int = 190000  # Daily token safety limit

    # Token Optimization & Context Pruning
    MAX_CANDIDATES_FOR_LLM: int = 9  # Limit to top 9 candidates to stay well within 8K TPM
    MAX_COMPLETION_TOKENS: int = 1500  # Output token ceiling for 6 concise recommendations without JSON truncation
    CACHE_TTL_SECONDS: int = 3600  # 1-hour in-memory response cache to save tokens & requests

    # Data Paths
    RAW_DATA_PATH: Path = PROJECT_ROOT / os.getenv("RAW_DATA_PATH", "data/raw/zomato_raw.parquet")
    PROCESSED_DATA_PATH: Path = PROJECT_ROOT / os.getenv("PROCESSED_DATA_PATH", "data/processed/restaurants.parquet")
    DUCKDB_PATH: Path = PROJECT_ROOT / os.getenv("DUCKDB_PATH", "data/processed/zomato.duckdb")

    # API Server Settings
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Hugging Face Dataset identifier
    HF_DATASET_ID: str = "ManikaSaini/zomato-restaurant-recommendation"

    @property
    def has_groq_key(self) -> bool:
        return bool(self.GROQ_API_KEY and self.GROQ_API_KEY != "your_groq_api_key_here")

    @property
    def has_gemini_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY != "your_gemini_api_key_here")

    @property
    def has_openai_key(self) -> bool:
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your_openai_api_key_here")

    @property
    def active_llm_provider(self) -> str:
        if self.DEFAULT_LLM_PROVIDER == "groq" and self.has_groq_key:
            return "groq"
        if self.DEFAULT_LLM_PROVIDER == "gemini" and self.has_gemini_key:
            return "gemini"
        if self.DEFAULT_LLM_PROVIDER == "openai" and self.has_openai_key:
            return "openai"
        if self.has_groq_key:
            return "groq"
        if self.has_gemini_key:
            return "gemini"
        if self.has_openai_key:
            return "openai"
        return "none"  # Triggers deterministic fallback mode


# Singleton instance
settings = Settings()
