"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
import re
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Centralized configuration for the FastAPI backend."""

    APP_NAME: str = "AI-Assisted Legal Case Guidance and Prediction System"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://[::1]:5173"

    GEMINI_API_KEY: str = ""
    GEMINI_API_KEYS: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash"

    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    RANDOM_FOREST_MODEL_DIR: str = "data/models/random_forest_exp3"
    RETRIEVAL_DATA_DIR: str = "data/retrieval/Case_Files"
    RETRIEVAL_INDEX_DIR: str = "data/retrieval_index"
    RETRIEVAL_TOP_K: int = 5

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a clean list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def gemini_api_keys_list(self) -> List[str]:
        """Return ordered, deduplicated Gemini API keys from GEMINI_API_KEY and GEMINI_API_KEYS."""
        raw_items = re.split(r"[\s,;]+", f"{self.GEMINI_API_KEY} {self.GEMINI_API_KEYS}")
        seen: set[str] = set()
        ordered: List[str] = []
        for item in raw_items:
            key = item.strip().strip('"').strip("'")
            upper = key.upper()
            if (
                not key
                or upper.startswith(("PASTE_", "REPLACE_", "YOUR_", "<"))
                or upper.endswith(">")
            ):
                continue
            if key not in seen:
                seen.add(key)
                ordered.append(key)
        return ordered


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
