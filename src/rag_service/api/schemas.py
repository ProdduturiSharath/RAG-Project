"""Pydantic request and response models for the public API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourcePayload(BaseModel):
    uri: str = ""
    path: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    fragment: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AccessPolicyPayload(BaseModel):
    public: bool = False
    principals: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SectionPayload(BaseModel):
    text: str = ""
    heading: str | None = None
    level: int = Field(default=0, ge=0)
    section_path: list[str] = Field(default_factory=list)
    page_number: int | None = Field(default=None, ge=1)
    page_metadata: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    section_id: str | None = None
    parent_section_id: str | None = None


class IngestDocumentRequest(BaseModel):
    document_id: str = Field(min_length=1)
    title: str | None = None
    version: str | None = None
    content_hash: str | None = None
    source: SourcePayload | None = None
    access_policy: AccessPolicyPayload | None = None
    sections: list[SectionPayload] = Field(default_factory=list)
    text: str | None = None


class IngestDocumentResponse(BaseModel):
    document_id: str
    version: str
    content_hash: str
    ingestion_id: str | None
    chunk_count: int
    already_ingested: bool
    revision: int = 1


class QueryRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)
    candidate_k: int | None = Field(default=None, ge=1, le=100)
    alpha: float | None = Field(default=None, ge=0, le=1)
    document_ids: list[str] = Field(default_factory=list)
    principal: str | None = None
    groups: list[str] = Field(default_factory=list)
    product_version: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CitationResponse(BaseModel):
    chunk_id: str
    document_id: str
    version: str
    source_uri: str | None = None
    page_number: int | None = None
    section_path: list[str] = Field(default_factory=list)
    excerpt: str = ""
    revision: int = 1


class MatchResponse(BaseModel):
    chunk_id: str
    document_id: str
    version: str
    text: str
    section_path: list[str] = Field(default_factory=list)
    page_number: int | None = None
    dense_score: float
    sparse_score: float
    hybrid_score: float
    rerank_score: float | None = None
    rank: int


class QueryResponse(BaseModel):
    query: str
    answer: str
    citations: list[CitationResponse] = Field(default_factory=list)
    matches: list[MatchResponse] = Field(default_factory=list)
    confidence: float
    abstained: bool


class HealthResponse(BaseModel):
    status: str
    environment: str
    indexed_chunks: int


class JobResponse(BaseModel):
    id: str
    kind: str
    status: str
    attempts: int
    error: str | None = None
    result: dict[str, Any] | None = None
    created_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None


__all__ = [
    "AccessPolicyPayload",
    "CitationResponse",
    "HealthResponse",
    "IngestDocumentRequest",
    "IngestDocumentResponse",
    "JobResponse",
    "MatchResponse",
    "QueryRequest",
    "QueryResponse",
    "SectionPayload",
    "SourcePayload",
]
