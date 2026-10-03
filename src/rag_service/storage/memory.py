"""In-memory versioned store used by the shared lifecycle contract tests."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from rag_service.domain import (
    AccessPolicy,
    DocumentIdentity,
    DocumentSection,
    DocumentVersion,
    IngestionResult,
)
from rag_service.ingestion.chunking import DeterministicChunker, content_hash_for_sections
from rag_service.ingestion.ports import Embedder, SparseEncoder


@dataclass(slots=True)
class _Revision:
    result: IngestionResult
    parser_config_hash: str
    chunker_config_hash: str
    embedder_id: str
    status: str


class InMemoryVersionedStore:
    """Mirror the Postgres lifecycle semantics without external services."""

    def __init__(
        self,
        chunker: DeterministicChunker,
        *,
        embedder: Embedder,
        sparse_encoder: SparseEncoder,
        embedder_id: str = "hash-v1",
        parser_config_hash: str = "parser-v1",
    ) -> None:
        self.chunker = chunker
        self.embedder = embedder
        self.sparse_encoder = sparse_encoder
        self.embedder_id = embedder_id
        self.parser_config_hash = parser_config_hash
        self.chunker_config_hash = hashlib.sha256(
            json.dumps(
                {
                    "max_tokens": chunker.config.max_tokens,
                    "overlap_tokens": chunker.config.overlap_tokens,
                    "detect_markdown_headings": chunker.config.detect_markdown_headings,
                },
                sort_keys=True,
            ).encode()
        ).hexdigest()
        self._revisions: dict[tuple[str, str], list[_Revision]] = {}
        self._embeddings: dict[tuple[str, str], tuple[tuple[float, ...], dict[str, float]]] = {}
        self._acl: dict[tuple[str, str], AccessPolicy | None] = {}

    def ingest(
        self,
        document: DocumentIdentity | str,
        sections: Iterable[DocumentSection | Mapping[str, Any]] | str,
        version: DocumentVersion | str | None = None,
        *,
        content_hash: str | None = None,
        access_policy: AccessPolicy | None = None,
        skip_unchanged: bool = True,
        fail_after: str | None = None,
        **_: Any,
    ) -> IngestionResult:
        identity = (
            document if isinstance(document, DocumentIdentity) else DocumentIdentity(document)
        )
        policy = access_policy if access_policy is not None else identity.access_policy
        values = sections if isinstance(sections, str) else list(sections)
        calculated = content_hash_for_sections(
            (DocumentSection(text=values),) if isinstance(values, str) else values
        )
        if isinstance(version, DocumentVersion):
            version_label = version.version
            calculated = version.content_hash
        elif isinstance(version, str):
            version_label = version
        else:
            version_label = calculated
        effective_hash = content_hash or calculated
        prepared = self.chunker.prepare_sections(values)
        chunks = self.chunker.chunk(
            prepared,
            document_id=identity.document_id,
            version=version_label,
            access_policy=policy,
        )
        key = (identity.document_id, version_label)
        revisions = self._revisions.setdefault(key, [])
        active = next((item for item in revisions if item.status == "active"), None)
        if (
            skip_unchanged
            and active
            and active.result.content_hash == effective_hash
            and active.parser_config_hash == self.parser_config_hash
            and active.chunker_config_hash == self.chunker_config_hash
            and active.embedder_id == self.embedder_id
        ):
            self._acl[key] = policy
            return _with_policy(active.result, policy, already_ingested=True)

        vectors = self._vectors(chunks, fail_after)
        revision = max((item.result.revision for item in revisions), default=0) + 1
        result = IngestionResult(
            document_id=identity.document_id,
            version=version_label,
            content_hash=effective_hash,
            chunks=chunks,
            access_policy=policy,
            dense_vectors=tuple(vectors[chunk.content_hash or ""][0] for chunk in chunks),
            sparse_vectors=tuple(vectors[chunk.content_hash or ""][1] for chunk in chunks),
            revision=revision,
        )
        if fail_after == "chunks":
            raise RuntimeError("injected failure after chunk insertion")
        for item in revisions:
            if item.status == "active":
                item.status = "superseded"
        revisions.append(
            _Revision(
                result=result,
                parser_config_hash=self.parser_config_hash,
                chunker_config_hash=self.chunker_config_hash,
                embedder_id=self.embedder_id,
                status="active",
            )
        )
        self._acl[key] = policy
        return result

    def delete_document(self, document_id: str, product_version: str | None = None) -> int:
        count = 0
        for (stored_document, stored_version), revisions in self._revisions.items():
            if stored_document != document_id or (
                product_version is not None and stored_version != product_version
            ):
                continue
            for item in revisions:
                if item.status in {"active", "superseded", "building"}:
                    item.status = "deleted"
                    count += 1
        return count

    def active_revision(self, document_id: str, product_version: str) -> dict[str, Any] | None:
        revision = next(
            (
                item
                for item in self._revisions.get((document_id, product_version), ())
                if item.status == "active"
            ),
            None,
        )
        if revision is None:
            return None
        return {
            "revision": revision.result.revision,
            "content_hash": revision.result.content_hash,
            "status": revision.status,
            "embedder_id": revision.embedder_id,
        }

    def _vectors(self, chunks: tuple[Any, ...], fail_after: str | None) -> dict[str, Any]:
        missing = [
            chunk
            for chunk in chunks
            if (chunk.content_hash, self.embedder_id) not in self._embeddings
        ]
        if missing:
            dense = self.embedder.embed(tuple(chunk.text for chunk in missing))
            sparse = self.sparse_encoder.encode(tuple(chunk.text for chunk in missing))
            for chunk, dense_vector, sparse_vector in zip(missing, dense, sparse, strict=True):
                self._embeddings[(chunk.content_hash or "", self.embedder_id)] = (
                    tuple(float(value) for value in dense_vector),
                    {str(key): float(value) for key, value in sparse_vector.items()},
                )
        if fail_after == "embeddings":
            raise RuntimeError("injected failure after embedding insertion")
        return {
            chunk.content_hash or "": self._embeddings[(chunk.content_hash or "", self.embedder_id)]
            for chunk in chunks
        }


def _with_policy(
    result: IngestionResult,
    policy: AccessPolicy | None,
    *,
    already_ingested: bool,
) -> IngestionResult:
    return IngestionResult(
        document_id=result.document_id,
        version=result.version,
        content_hash=result.content_hash,
        chunks=tuple(
            chunk.__class__(
                **{
                    field: getattr(chunk, field)
                    for field in chunk.__dataclass_fields__
                    if field != "access_policy"
                },
                access_policy=policy,
            )
            for chunk in result.chunks
        ),
        access_policy=policy,
        already_ingested=already_ingested,
        revision=result.revision,
    )


__all__ = ["InMemoryVersionedStore"]
