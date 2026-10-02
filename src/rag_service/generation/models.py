"""Contracts between retrieval and an answer generator."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from rag_service.retrieval import Citation, ScoredChunk


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    query: str
    matches: tuple[ScoredChunk, ...]
    max_context_chars: int = 18_000

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("query cannot be empty")
        if self.max_context_chars < 1:
            raise ValueError("max_context_chars must be positive")
        object.__setattr__(self, "matches", tuple(self.matches))


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    answer: str
    citations: tuple[Citation, ...] = ()
    confidence: float = 0.0
    abstained: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "citations", tuple(self.citations))
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between zero and one")


class AnswerGenerator(Protocol):
    async def generate(self, request: GenerationRequest) -> GeneratedAnswer:
        """Generate an answer that is constrained by the supplied evidence."""

    def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Yield answer text incrementally."""


__all__ = ["AnswerGenerator", "GeneratedAnswer", "GenerationRequest"]
