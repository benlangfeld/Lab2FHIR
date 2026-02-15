"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/lab2fhir",
        description="PostgreSQL database URL",
    )

    # Storage
    pdf_storage_path: str = Field(
        default="./storage/pdfs",
        description="Path for storing source PDF files",
    )
    bundle_storage_path: str = Field(
        default="./storage/bundles",
        description="Path for storing generated FHIR bundles",
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Enable auto-reload in development")
    debug: bool = Field(default=True, description="Enable debug mode")

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # LLM Configuration (optional - for parsing service)
    llm_provider: str | None = Field(default=None, description="LLM provider (e.g., openai)")
    llm_api_key: str | None = Field(default=None, description="LLM API key")
    llm_model: str | None = Field(default=None, description="LLM model name")
    llm_base_url: str | None = Field(default=None, description="LLM API base URL")

    # Optional: FHIR Server Integration (P5 feature)
    fhir_base_url: str | None = Field(default=None, description="FHIR server base URL")
    fhir_auth_type: Literal["none", "basic", "bearer"] = Field(
        default="none", description="FHIR authentication type"
    )
    fhir_auth_token: str | None = Field(default=None, description="FHIR authentication token")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
