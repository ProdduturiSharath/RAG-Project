"""Value objects shared by retrieval adapters and the API layer."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

from rag_service.domain import Chunk


@dataclass(frozen=True, slots=True)
class RetrievalFilters:
    """Safe, explicit filters accepted by a retrieval request.

    Arbitrary Pinecone filter expressions are intentionally not accepted at the
    HTTP boundary.  Adapters can translate these fields into their own filter
    syntax after applying the same authorization rules.
    """

    document_ids: tuple[str, ...] = ()
    principal: str | None = None
    groups: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    product_version: str | None = None
    version_mode: Literal["none", "explicit", "auto"] | None = None
    version_selector: Literal["exact", "latest", "all"] = "exact"
    scopes: tuple[tuple[str, str], ...] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "document_ids", tuple(self.document_ids))
        object.__setattr__(self, "groups", tuple(self.groups))
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True, slots=True)
class ScoredChunk:
    """A chunk with component scores retained for debugging and evaluation."""

    chunk: Chunk
    dense_score: float = 0.0
    sparse_score: float = 0.0
    hybrid_score: float = 0.0
    rerank_score: float | None = None
    rank: int = 0

    @property
    def final_score(self) -> float:
        return self.rerank_score if self.rerank_score is not None else self.hybrid_score

    @property
    def text(self) -> str:
        return self.chunk.text

    def citation(self) -> Citation:
        source = self.chunk.source
        return Citation(
            chunk_id=self.chunk.chunk_id,
            document_id=self.chunk.document_id,
            version=self.chunk.version,
            source_uri=source.stable_uri if source else None,
            page_number=self.chunk.page_number,
            section_path=self.chunk.section_path,
            excerpt=self.chunk.text,
            revision=self.chunk.revision,
        )


@dataclass(frozen=True, slots=True)
class Citation:
    """A compact, client-safe reference to the evidence behind an answer."""

    chunk_id: str
    document_id: str
    version: str
    source_uri: str | None = None
    page_number: int | None = None
    section_path: tuple[str, ...] = ()
    excerpt: str = ""
    revision: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "section_path", tuple(self.section_path))

    @property
    def product_version(self) -> str:
        return self.version


@dataclass(frozen=True, slots=True)
class ScopeResult:
    filters: RetrievalFilters
    status: Literal["resolved", "ambiguous"] = "resolved"
    versions: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class StageTrace:
    stage: str
    candidates: tuple[dict[str, Any], ...]
    elapsed_ms: float
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    matches: tuple[ScoredChunk, ...]
    scope: ScopeResult
    trace_id: str
    stages: tuple[StageTrace, ...]


__all__ = ["Citation", "RetrievalFilters", "ScoredChunk"]
