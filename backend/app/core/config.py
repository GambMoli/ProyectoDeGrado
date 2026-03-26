from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_KNOWLEDGE_DATASETS_DIR = str(
    Path(__file__).resolve().parents[3] / "knowledge" / "datasets"
)


class Settings(BaseSettings):
    app_name: str = "Calculus Tutor API"
    environment: str = "development"
    debug: bool = False
    api_prefix: str = "/api"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/calc_tutor"
    )

    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:4173",
            "http://localhost:8080",
        ]
    ) # Esto es por si corren el front en otro puerto xd

    ollama_enabled: bool = False
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout_seconds: int = 25

    ocr_provider: str = "tesseract"
    ocr_language: str = "eng"
    tesseract_cmd: str | None = None
    max_upload_size_mb: int = 5
    knowledge_datasets_dir: str = DEFAULT_KNOWLEDGE_DATASETS_DIR
    rag_top_k: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
