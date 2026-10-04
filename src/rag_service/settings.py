"""Typed application settings loaded from the environment.

Settings are validated at the application boundary with ``pydantic-settings``.
The explicit aliases preserve the existing ``RAG_*`` environment contract while
allowing tests and workers to construct a validated object directly.
"""

from __future__ import annotations

from typing import Literal

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
    dense_model: str = Field(
        default="bge-small",
        validation_alias=AliasChoices("RAG_DENSE_MODEL", "dense_model"),
    )
    metadata_prefixed_embeddings: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "RAG_METADATA_PREFIXED_EMBEDDINGS", "metadata_prefixed_embeddings"
        ),
    )
    fusion_method: Literal["rrf", "weighted"] = Field(
        default="rrf",
        validation_alias=AliasChoices("RAG_FUSION_METHOD", "fusion_method"),
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L6-v2",
        validation_alias=AliasChoices("RAG_RERANKER_MODEL", "reranker_model"),
    )
    rerank_top_n: int = Field(
        default=30,
        validation_alias=AliasChoices("RAG_RERANK_TOP_N", "rerank_top_n"),
    )
    version_mode: Literal["none", "explicit", "auto"] = Field(
        default="none",
        validation_alias=AliasChoices("RAG_VERSION_MODE", "version_mode"),
    )
    version_selector: Literal["exact", "latest", "all"] = Field(
        default="exact",
        validation_alias=AliasChoices("RAG_VERSION_SELECTOR", "version_selector"),
    )
    parent_expansion: bool = Field(
        default=True,
        validation_alias=AliasChoices("RAG_PARENT_EXPANSION", "parent_expansion"),
    )
    max_context_chars: int = Field(
        default=18_000,
        validation_alias=AliasChoices("RAG_MAX_CONTEXT_CHARS", "max_context_chars"),
    )
    storage_backend: Literal["memory", "postgres"] = Field(
        default="memory",
        validation_alias=AliasChoices("RAG_STORAGE_BACKEND", "storage_backend"),
    )
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/evidence_rag",
        validation_alias=AliasChoices("RAG_DATABASE_URL", "database_url"),
    )
    embedder_id: str = Field(
        default="bge-small-en-v1.5",
        min_length=1,
        validation_alias=AliasChoices("RAG_EMBEDDER_ID", "embedder_id"),
    )
    embedding_batch_size: int = Field(
        default=64,
        validation_alias=AliasChoices("RAG_EMBEDDING_BATCH_SIZE", "embedding_batch_size"),
    )
    migrations_path: str = Field(
        default="migrations",
        min_length=1,
        validation_alias=AliasChoices("RAG_MIGRATIONS_PATH", "migrations_path"),
    )
    job_poll_seconds: float = Field(
        default=1.0,
        validation_alias=AliasChoices("RAG_JOB_POLL_SECONDS", "job_poll_seconds"),
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
        if self.rerank_top_n < 1:
            raise ValueError("rerank_top_n must be positive")
        if self.max_context_chars < 1:
            raise ValueError("max_context_chars must be positive")
        if self.embedding_batch_size < 1:
            raise ValueError("embedding_batch_size must be positive")
        if self.job_poll_seconds <= 0:
            raise ValueError("job_poll_seconds must be positive")
        return self

    @classmethod
    def from_env(cls) -> Settings:
        """Compatibility constructor for callers that used the old API."""

        return cls()


def load_settings() -> Settings:
    """Load settings at the application boundary."""

    return Settings.from_env()


__all__ = ["Settings", "load_settings"]
