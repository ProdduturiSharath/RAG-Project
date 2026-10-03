"""Typed application settings loaded from the environment.

Settings are validated at the application boundary with ``pydantic-settings``.
The explicit aliases preserve the existing ``RAG_*`` environment contract while
allowing tests and workers to construct a validated object directly.
"""

from __future__ import annotations

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the API and its local adapters."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("RAG_ENV", "environment"),
    )
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("RAG_LOG_LEVEL", "log_level"),
    )
    chunk_max_tokens: int = Field(
        default=220,
        validation_alias=AliasChoices("RAG_CHUNK_MAX_TOKENS", "chunk_max_tokens"),
    )
    chunk_overlap_tokens: int = Field(
        default=35,
        validation_alias=AliasChoices("RAG_CHUNK_OVERLAP_TOKENS", "chunk_overlap_tokens"),
    )
    retrieval_top_k: int = Field(
        default=5,
        validation_alias=AliasChoices("RAG_RETRIEVAL_TOP_K", "retrieval_top_k"),
    )
    retrieval_candidate_k: int = Field(
        default=30,
        validation_alias=AliasChoices("RAG_RETRIEVAL_CANDIDATE_K", "retrieval_candidate_k"),
    )
    hybrid_alpha: float = Field(
        default=0.55,
        validation_alias=AliasChoices("RAG_HYBRID_ALPHA", "hybrid_alpha"),
    )
    max_context_chars: int = Field(
        default=18_000,
        validation_alias=AliasChoices("RAG_MAX_CONTEXT_CHARS", "max_context_chars"),
    )

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_ranges(self) -> Settings:
        if self.chunk_max_tokens < 1:
            raise ValueError("chunk_max_tokens must be positive")
        if not 0 <= self.chunk_overlap_tokens < self.chunk_max_tokens:
            raise ValueError("chunk_overlap_tokens must be between zero and chunk_max_tokens")
        if self.retrieval_top_k < 1:
            raise ValueError("retrieval_top_k must be positive")
        if self.retrieval_candidate_k < self.retrieval_top_k:
            raise ValueError("retrieval_candidate_k must be at least retrieval_top_k")
        if not 0 <= self.hybrid_alpha <= 1:
            raise ValueError("hybrid_alpha must be between zero and one")
        if self.max_context_chars < 1:
            raise ValueError("max_context_chars must be positive")
        return self

    @classmethod
    def from_env(cls) -> Settings:
        """Compatibility constructor for callers that used the old API."""

        return cls()


def load_settings() -> Settings:
    """Load settings at the application boundary."""

    return Settings.from_env()


__all__ = ["Settings", "load_settings"]
