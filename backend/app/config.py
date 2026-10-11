from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime configuration. Values come from environment variables or backend/.env."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    auth_mode: Literal["local", "jwt"] = "local"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    log_level: str = "INFO"

    database_url: str = "sqlite:///./data/runtime/sakhisahay.db"

    llm_provider: Literal["gemini", "none"] = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    llm_timeout_seconds: float = 40.0

    embedding_model: str = "intfloat/multilingual-e5-small"
    qdrant_path: str = "./data/runtime/qdrant"
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "sakhisahay_knowledge"

    retrieval_top_k: int = Field(default=6, ge=1, le=20)
    retrieval_min_score: float = Field(default=0.80, ge=0.0, le=1.0)

    knowledge_dir: Path = BACKEND_DIR / "data" / "knowledge"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    def resolve_path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else (BACKEND_DIR / path).resolve()

    @property
    def resolved_database_url(self) -> str:
        prefix = "sqlite:///"
        if self.database_url.startswith(prefix) and not self.database_url.startswith(prefix + "/"):
            relative = self.database_url[len(prefix) :]
            if relative.startswith("./"):
                relative = relative[2:]
            return prefix + str((BACKEND_DIR / relative).resolve())
        return self.database_url

    @property
    def llm_enabled(self) -> bool:
        return self.llm_provider == "gemini" and bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
