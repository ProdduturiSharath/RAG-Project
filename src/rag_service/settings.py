"""Application settings with a deliberately small environment surface.

The first local slice does not require provider credentials.  Keeping settings
in a plain dataclass also means workers and tests can construct an application
without loading a global configuration object.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime configuration for the API and its local adapters."""

    environment: str = "development"
    log_level: str = "INFO"
    chunk_max_tokens: int = 220
    chunk_overlap_tokens: int = 35
    retrieval_top_k: int = 5
    retrieval_candidate_k: int = 30
    hybrid_alpha: float = 0.55
    max_context_chars: int = 18_000

    def __post_init__(self) -> None:
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

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            environment=os.getenv("RAG_ENV", "development"),
            log_level=os.getenv("RAG_LOG_LEVEL", "INFO").upper(),
            chunk_max_tokens=_int_env("RAG_CHUNK_MAX_TOKENS", 220),
            chunk_overlap_tokens=_int_env("RAG_CHUNK_OVERLAP_TOKENS", 35),
            retrieval_top_k=_int_env("RAG_RETRIEVAL_TOP_K", 5),
            retrieval_candidate_k=_int_env("RAG_RETRIEVAL_CANDIDATE_K", 30),
            hybrid_alpha=_float_env("RAG_HYBRID_ALPHA", 0.55),
            max_context_chars=_int_env("RAG_MAX_CONTEXT_CHARS", 18_000),
        )


def load_settings() -> Settings:
    """Load settings at the application boundary."""

    return Settings.from_env()


__all__ = ["Settings", "load_settings"]
