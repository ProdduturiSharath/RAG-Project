"""A small provider-independent ingestion pipeline."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace
from typing import Any

from rag_service.domain import (
    AccessPolicy,
    Chunk,
    DocumentIdentity,
    DocumentSection,
    DocumentVersion,
    IngestionResult,
    SourceLocation,
)

from .chunking import DeterministicChunker, content_hash_for_sections
from .ports import Embedder, IndexWriter, Parser, SparseEncoder

SectionInput = DocumentSection | Mapping[str, Any]


class IngestionPipeline:
    """Chunk parsed sections and optionally hand them to index adapters.

    The default pipeline has no network or provider dependency.  Embedders,
    sparse encoders, and writers are optional and are called only when supplied
    by the application.  A small in-memory result cache makes repeated calls
    for the same ``document/version/content_hash`` safe to retry; no durable
    state is implied by this cache.
    """

    def __init__(
        self,
        chunker: DeterministicChunker | None = None,
        *,
        embedder: Embedder | None = None,
        sparse_encoder: SparseEncoder | None = None,
        index_writer: IndexWriter | None = None,
        cache_results: bool = True,
    ) -> None:
        self.chunker = chunker or DeterministicChunker()
        self.embedder = embedder
        self.sparse_encoder = sparse_encoder
        self.index_writer = index_writer
        self.cache_results = cache_results
        self._results: dict[tuple[str, str, str], IngestionResult] = {}

    def ingest(
        self,
        document: DocumentIdentity | str,
        sections: Iterable[SectionInput] | str,
        version: DocumentVersion | str | None = None,
        *,
        content_hash: str | None = None,
        source: SourceLocation | None = None,
        access_policy: AccessPolicy | None = None,
        skip_unchanged: bool = True,
    ) -> IngestionResult:
        """Ingest parsed sections and return a deterministic result.

        ``version`` may be a plain version label or a :class:`DocumentVersion`.
        If omitted, the calculated content hash is used as the version, making
        retries naturally idempotent.  An explicit ``content_hash`` is useful
        when an upstream parser already has a canonical hash.
        """

        identity = self._identity(document)
        document_id = identity.document_id
        effective_source = source or identity.source
        effective_policy = access_policy or identity.access_policy

        # Materialize once so generators are hashed and chunked consistently.
        section_values: list[SectionInput] | str
        if isinstance(sections, str):
            section_values = sections
            calculated_hash = content_hash_for_sections((DocumentSection(text=sections),))
        else:
            section_values = list(sections)
            calculated_hash = content_hash_for_sections(section_values)

        version_label, supplied_hash = self._version_values(version, document_id)
        effective_hash = content_hash or supplied_hash or calculated_hash
        if not effective_hash.strip():
            raise ValueError("content_hash cannot be empty")
        if version_label is None:
            version_label = effective_hash

        cache_key = (document_id, version_label, effective_hash)
        if self.cache_results and skip_unchanged and cache_key in self._results:
            return replace(self._results[cache_key], already_ingested=True)

        chunks = self.chunker.chunk(
            section_values,
            document_id=document_id,
            version=version_label,
            access_policy=effective_policy,
        )
        texts = tuple(chunk.text for chunk in chunks)
        dense_vectors = self._dense_vectors(texts)
        sparse_vectors = self._sparse_vectors(texts)

        self._write(chunks, dense_vectors, sparse_vectors)
        result = IngestionResult(
            document_id=document_id,
            version=version_label,
            content_hash=effective_hash,
            chunks=chunks,
            ingestion_id=self._ingestion_id(cache_key),
            source=effective_source,
            access_policy=effective_policy,
            dense_vectors=dense_vectors,
            sparse_vectors=sparse_vectors,
        )
        if self.cache_results:
            self._results[cache_key] = result
        return result

    def ingest_sections(
        self,
        sections: Iterable[SectionInput] | str,
        *,
        document_id: str,
        version: DocumentVersion | str | None = None,
        content_hash: str | None = None,
        source: SourceLocation | None = None,
        access_policy: AccessPolicy | None = None,
        skip_unchanged: bool = True,
    ) -> IngestionResult:
        """Keyword-oriented convenience wrapper for callers with raw IDs."""

        return self.ingest(
            document_id,
            sections,
            version,
            content_hash=content_hash,
            source=source,
            access_policy=access_policy,
            skip_unchanged=skip_unchanged,
        )

    def ingest_source(
        self,
        document: DocumentIdentity | str,
        source: SourceLocation,
        parser: Parser,
        version: DocumentVersion | str | None = None,
        *,
        content_hash: str | None = None,
        access_policy: AccessPolicy | None = None,
        skip_unchanged: bool = True,
    ) -> IngestionResult:
        """Parse a source through a supplied adapter, then ingest its sections."""

        return self.ingest(
            document,
            parser.parse(source),
            version,
            content_hash=content_hash,
            source=source,
            access_policy=access_policy,
            skip_unchanged=skip_unchanged,
        )

    # ``run`` reads naturally in applications that treat ingestion as a job.
    run = ingest

    def delete_document(self, document_id: str, product_version: str | None = None) -> int:
        """Delete local indexed chunks and forget process-local idempotency state."""

        deleted = 0
        if self.index_writer is not None:
            delete = getattr(self.index_writer, "delete_document", None)
            if delete is not None:
                deleted = int(delete(document_id, product_version))
        keys = [
            key
            for key in self._results
            if key[0] == document_id and (product_version is None or key[1] == product_version)
        ]
        for key in keys:
            del self._results[key]
        return deleted

    @staticmethod
    def _identity(document: DocumentIdentity | str) -> DocumentIdentity:
        if isinstance(document, DocumentIdentity):
            return document
        if isinstance(document, str):
            return DocumentIdentity(document_id=document)
        raise TypeError("document must be a DocumentIdentity or document ID string")

    @staticmethod
    def _version_values(
        version: DocumentVersion | str | None,
        document_id: str,
    ) -> tuple[str | None, str | None]:
        if version is None:
            return None, None
        if isinstance(version, DocumentVersion):
            if version.document_id != document_id:
                raise ValueError(
                    "DocumentVersion.document_id does not match the document identity"
                )
            return version.version, version.content_hash
        if isinstance(version, str):
            if not version.strip():
                raise ValueError("version cannot be empty")
            return version, None
        raise TypeError("version must be a string, DocumentVersion, or None")

    def _dense_vectors(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        if self.embedder is None or not texts:
            return ()
        vectors = tuple(
            tuple(float(value) for value in vector)
            for vector in self.embedder.embed(texts)
        )
        self._validate_vector_count("dense", len(texts), len(vectors))
        return vectors

    def _sparse_vectors(
        self,
        texts: Sequence[str],
    ) -> tuple[Mapping[str, float], ...]:
        if self.sparse_encoder is None or not texts:
            return ()
        vectors = tuple(
            {str(key): float(value) for key, value in vector.items()}
            for vector in self.sparse_encoder.encode(texts)
        )
        self._validate_vector_count("sparse", len(texts), len(vectors))
        return vectors

    @staticmethod
    def _validate_vector_count(kind: str, expected: int, actual: int) -> None:
        if expected != actual:
            raise ValueError(
                f"{kind} encoder returned {actual} vectors for {expected} chunks"
            )

    def _write(
        self,
        chunks: Sequence[Chunk],
        dense_vectors: Sequence[Sequence[float]],
        sparse_vectors: Sequence[Mapping[str, float]],
    ) -> None:
        if self.index_writer is None:
            return
        if dense_vectors or sparse_vectors:
            self.index_writer.write(
                chunks,
                dense_vectors=dense_vectors,
                sparse_vectors=sparse_vectors,
            )
        else:
            # This also supports minimal writers whose ``write`` method only
            # accepts the chunk batch.
            self.index_writer.write(chunks)

    @staticmethod
    def _ingestion_id(cache_key: tuple[str, str, str]) -> str:
        payload = "\x1f".join(cache_key).encode("utf-8")
        return f"ingestion-{hashlib.sha256(payload).hexdigest()}"


__all__ = ["IngestionPipeline", "SectionInput"]
