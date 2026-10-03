"""Lossless chunk payloads and shared ingestion preparation."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from typing import Any

from rag_service.domain import (
    AccessPolicy,
    Chunk,
    DocumentIdentity,
    DocumentSection,
    DocumentVersion,
    SourceLocation,
)
from rag_service.ingestion.chunking import DeterministicChunker, content_hash_for_sections

VectorPair = tuple[tuple[float, ...], dict[str, float]]


def config_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"))
                          .encode()).hexdigest()


def chunk_from_payload(payload: dict[str, Any]) -> Chunk:
    values = dict(payload)
    if values.get("source"):
        values["source"] = SourceLocation(**values["source"])
    if values.get("access_policy") is not None:
        values["access_policy"] = AccessPolicy(**values["access_policy"])
    return Chunk(**values)


def chunk_to_payload(chunk: Chunk) -> dict[str, Any]:
    values = asdict(chunk)
    if chunk.source is not None:
        values["source"] = asdict(chunk.source)
    if chunk.access_policy is not None:
        values["access_policy"] = asdict(chunk.access_policy)
    return values


@dataclass(frozen=True)
class PreparedDocument:
    identity: DocumentIdentity
    version: str
    content_hash: str
    chunks: tuple[Chunk, ...]
    source: SourceLocation | None
    policy: AccessPolicy | None


def prepare_document(
    chunker: DeterministicChunker,
    document: DocumentIdentity | str,
    sections: Iterable[DocumentSection | Mapping[str, Any]] | str,
    version: DocumentVersion | str | None,
    content_hash: str | None,
    source: SourceLocation | None,
    access_policy: AccessPolicy | None,
) -> PreparedDocument:
    identity = document if isinstance(document, DocumentIdentity) else DocumentIdentity(document)
    source = source or identity.source
    policy = access_policy if access_policy is not None else identity.access_policy
    parsed = chunker.prepare_sections(sections)
    parsed = [replace(section, source=section.source or source) for section in parsed]
    calculated = content_hash_for_sections(parsed)
    if isinstance(version, DocumentVersion):
        if version.document_id != identity.document_id:
            raise ValueError("DocumentVersion.document_id does not match document")
        content_hash = content_hash or version.content_hash
        version = version.version
    if content_hash is not None and content_hash != calculated:
        raise ValueError("supplied content_hash does not match parsed content")
    version = version if version is not None else calculated
    if not version.strip():
        raise ValueError("product_version cannot be empty")
    chunks = chunker.chunk(parsed, identity.document_id, version, access_policy=policy)
    if not chunks:
        raise ValueError("document must contain non-empty content")
    return PreparedDocument(identity, version, calculated, chunks, source, policy)


def validate_vectors(
    dense: Sequence[Sequence[float]], sparse: Sequence[Mapping[str, float]], count: int
) -> tuple[VectorPair, ...]:
    if len(dense) != count or len(sparse) != count:
        raise ValueError("embedding adapters returned the wrong vector count")
    dimensions = {len(vector) for vector in dense}
    if len(dimensions) != 1 or not 0 < next(iter(dimensions)) <= 16000:
        raise ValueError("inconsistent or unsupported embedding dimensions")
    if not all(math.isfinite(v) for vector in dense for v in vector):
        raise ValueError("embedding elements must be finite")
    return tuple((tuple(vector), dict(weights))
                 for vector, weights in zip(dense, sparse, strict=True))


def chunker_hash(chunker: DeterministicChunker) -> str:
    return config_hash({"implementation": "structured-v2", **asdict(chunker.config)})
