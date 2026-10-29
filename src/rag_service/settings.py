"""Typed application settings loaded from the environment.

Settings are validated at the application boundary with ``pydantic-settings``.
The explicit aliases preserve the existing ``RAG_*`` environment contract while
allowing tests and workers to construct a validated object directly.
"""

from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEVELOPMENT_JWT_SECRET = "phase7-local-development-secret-32bytes!"


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
    query_instruction: bool = Field(
        default=True,
        validation_alias=AliasChoices("RAG_QUERY_INSTRUCTION", "query_instruction"),
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
    generation_backend: Literal["extractive", "deepseek-flash"] = Field(
        default="extractive",
        validation_alias=AliasChoices("RAG_GENERATION_BACKEND", "generation_backend"),
    )
    extractive_minimum_score: float = Field(
        default=0.12,
        validation_alias=AliasChoices(
            "RAG_EXTRACTIVE_MINIMUM_SCORE", "extractive_minimum_score"
        ),
    )
    jwt_secret: str = Field(
        default=DEVELOPMENT_JWT_SECRET,
        min_length=32,
        validation_alias=AliasChoices("RAG_JWT_SECRET", "jwt_secret"),
    )
    jwt_algorithm: Literal["HS256"] = Field(
        default="HS256",
        validation_alias=AliasChoices("RAG_JWT_ALGORITHM", "jwt_algorithm"),
    )
    max_request_body_bytes: int = Field(
        default=262_144,
        validation_alias=AliasChoices("RAG_MAX_REQUEST_BODY_BYTES", "max_request_body_bytes"),
    )
    max_query_chars: int = Field(
        default=4_096,
        validation_alias=AliasChoices("RAG_MAX_QUERY_CHARS", "max_query_chars"),
    )
    max_document_chars: int = Field(
        default=200_000,
        validation_alias=AliasChoices("RAG_MAX_DOCUMENT_CHARS", "max_document_chars"),
    )
    max_section_chars: int = Field(
        default=50_000,
        validation_alias=AliasChoices("RAG_MAX_SECTION_CHARS", "max_section_chars"),
    )
    max_sections: int = Field(
        default=100,
        validation_alias=AliasChoices("RAG_MAX_SECTIONS", "max_sections"),
    )
    max_metadata_keys: int = Field(
        default=50,
        validation_alias=AliasChoices("RAG_MAX_METADATA_KEYS", "max_metadata_keys"),
    )
    max_metadata_depth: int = Field(
        default=4,
        validation_alias=AliasChoices("RAG_MAX_METADATA_DEPTH", "max_metadata_depth"),
    )
    rate_limit_requests: int = Field(
        default=60,
        validation_alias=AliasChoices("RAG_RATE_LIMIT_REQUESTS", "rate_limit_requests"),
    )
    rate_limit_window_seconds: float = Field(
        default=60.0,
        validation_alias=AliasChoices("RAG_RATE_LIMIT_WINDOW_SECONDS", "rate_limit_window_seconds"),
    )
    request_timeout_seconds: float = Field(
        default=30.0,
        validation_alias=AliasChoices("RAG_REQUEST_TIMEOUT_SECONDS", "request_timeout_seconds"),
    )
    database_connect_timeout_seconds: int = Field(
        default=5,
        validation_alias=AliasChoices(
            "RAG_DATABASE_CONNECT_TIMEOUT_SECONDS", "database_connect_timeout_seconds"
        ),
    )
    database_statement_timeout_ms: int = Field(
        default=30_000,
        validation_alias=AliasChoices(
            "RAG_DATABASE_STATEMENT_TIMEOUT_MS", "database_statement_timeout_ms"
        ),
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
        if not 0 <= self.extractive_minimum_score <= 1:
            raise ValueError("extractive_minimum_score must be between zero and one")
        if len(self.jwt_secret.encode("utf-8")) < 32:
            raise ValueError("jwt_secret must be at least 32 UTF-8 bytes")
        if (
            self.environment.casefold() in {"production", "prod"}
            and self.jwt_secret == DEVELOPMENT_JWT_SECRET
        ):
            raise ValueError("production deployments must set a unique jwt_secret")
        if self.max_request_body_bytes < 1 or self.max_query_chars < 1:
            raise ValueError("request and query limits must be positive")
        if self.max_document_chars < 1 or self.max_section_chars < 1:
            raise ValueError("document and section limits must be positive")
        if self.max_sections < 1 or self.max_metadata_keys < 1 or self.max_metadata_depth < 1:
            raise ValueError("document structure limits must be positive")
        if self.rate_limit_requests < 1 or self.rate_limit_window_seconds <= 0:
            raise ValueError("rate limit settings must be positive")
        if self.request_timeout_seconds <= 0:
            raise ValueError("request_timeout_seconds must be positive")
        if self.database_connect_timeout_seconds <= 0 or self.database_statement_timeout_ms <= 0:
            raise ValueError("database timeout settings must be positive")
        return self

    @classmethod
    def from_env(cls) -> Settings:
        """Compatibility constructor for callers that used the old API."""

        return cls()


def load_settings() -> Settings:
    """Load settings at the application boundary."""

    return Settings.from_env()


__all__ = ["Settings", "load_settings"]
