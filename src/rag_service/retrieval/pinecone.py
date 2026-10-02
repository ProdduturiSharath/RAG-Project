"""Pinecone adapter for the dual-vector retrieval contract.

The SDK is imported lazily so local development and unit tests do not require a
Pinecone account.  The adapter accepts an already-created index client, which
also keeps connection setup outside the domain and use-case layers.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping, Sequence
from typing import Any

from rag_service.domain import AccessPolicy, Chunk, SourceLocation

from .models import RetrievalFilters, ScoredChunk


def sparse_term_index(term: str) -> int:
    """Map a sparse term to a stable positive Pinecone integer index."""

    digest = hashlib.blake2b(term.encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(digest, "big") % 2_000_000_000


class PineconeHybridIndex:
    """Store dense and sparse values in one Pinecone index."""

    def __init__(
        self,
        index_client: Any,
        *,
        namespace: str | None = None,
        dense_dimensions: int | None = None,
    ) -> None:
        self.index_client = index_client
        self.namespace = namespace
        self.dense_dimensions = dense_dimensions

    @classmethod
    def from_environment(
        cls,
        index_name: str,
        *,
        namespace: str | None = None,
        dense_dimensions: int | None = None,
    ) -> PineconeHybridIndex:
        """Create a client using ``PINECONE_API_KEY`` without logging it."""

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is required for Pinecone indexing")
        try:
            from pinecone import Pinecone  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Pinecone support requires the optional 'pinecone' dependency"
            ) from exc
        client = Pinecone(api_key=api_key)
        return cls(
            client.Index(index_name),
            namespace=namespace,
            dense_dimensions=dense_dimensions,
        )

    @property
    def count(self) -> int:
        """Return the approximate namespace count when the SDK exposes it."""

        stats = self.index_client.describe_index_stats(namespace=self.namespace)
        if isinstance(stats, Mapping):
            namespaces = stats.get("namespaces", {}) or {}
            if self.namespace:
                namespace_stats = namespaces.get(self.namespace, {}) or {}
                return int(namespace_stats.get("vector_count", 0))
            return int(stats.get("total_vector_count", 0))
        namespaces = getattr(stats, "namespaces", {}) or {}
        if self.namespace:
            namespace_stats = namespaces.get(self.namespace, {}) or {}
            return int(getattr(namespace_stats, "vector_count", 0))
        return int(getattr(stats, "total_vector_count", 0))

    def upsert(
        self,
        chunks: Sequence[Chunk],
        *,
        dense_vectors: Sequence[Sequence[float]] = (),
        sparse_vectors: Sequence[Mapping[str, float]] = (),
    ) -> int:
        if dense_vectors and len(dense_vectors) != len(chunks):
            raise ValueError("dense vector count must match chunk count")
        if sparse_vectors and len(sparse_vectors) != len(chunks):
            raise ValueError("sparse vector count must match chunk count")
        if not dense_vectors and not sparse_vectors:
            raise ValueError("Pinecone upsert requires dense or sparse vectors")

        vectors: list[dict[str, Any]] = []
        for position, chunk in enumerate(chunks):
            vector: dict[str, Any] = {
                "id": chunk.chunk_id,
                "metadata": self._metadata_for(chunk),
            }
            if dense_vectors:
                vector["values"] = [float(value) for value in dense_vectors[position]]
            if sparse_vectors:
                vector["sparse_values"] = self._sparse_payload(sparse_vectors[position])
            vectors.append(vector)
        if vectors:
            self.index_client.upsert(vectors=vectors, namespace=self.namespace)
        return len(vectors)

    def write(
        self,
        chunks: Sequence[Chunk],
        *,
        dense_vectors: Sequence[Sequence[float]] = (),
        sparse_vectors: Sequence[Mapping[str, float]] = (),
    ) -> None:
        self.upsert(
            chunks,
            dense_vectors=dense_vectors,
            sparse_vectors=sparse_vectors,
        )

    def search(
        self,
        dense_vector: Sequence[float],
        sparse_vector: Mapping[str, float],
        *,
        top_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between zero and one")
        if not dense_vector and not sparse_vector:
            return ()

        query: dict[str, Any] = {
            "top_k": top_k,
            "include_metadata": True,
            "namespace": self.namespace,
        }
        if dense_vector:
            # Pinecone's hybrid score is a dot product. Scaling the query
            # components applies alpha without rewriting stored vectors.
            query["vector"] = [alpha * float(value) for value in dense_vector]
        elif self.dense_dimensions:
            query["vector"] = [0.0] * self.dense_dimensions
        if sparse_vector and alpha < 1:
            query["sparse_vector"] = self._sparse_payload(
                {term: (1.0 - alpha) * value for term, value in sparse_vector.items()}
            )
        pinecone_filter = self._filter_for(filters)
        if pinecone_filter:
            query["filter"] = pinecone_filter
        response = self.index_client.query(**query)
        raw_matches = (
            response.get("matches", [])
            if isinstance(response, Mapping)
            else response.matches
        )
        results: list[ScoredChunk] = []
        for rank, match in enumerate(raw_matches or (), start=1):
            metadata = self._match_metadata(match)
            chunk = self._chunk_from_metadata(self._match_id(match), metadata)
            score = float(self._value(match, "score", 0.0))
            results.append(
                ScoredChunk(
                    chunk=chunk,
                    hybrid_score=score,
                    rank=rank,
                )
            )
        return tuple(results)

    def delete_document(self, document_id: str, version: str | None = None) -> None:
        document_filter: dict[str, Any] = {"document_id": {"$eq": document_id}}
        if version is not None:
            document_filter["version"] = {"$eq": version}
        self.index_client.delete(filter=document_filter, namespace=self.namespace)

    @staticmethod
    def _sparse_payload(values: Mapping[str, float]) -> dict[str, list[Any]]:
        ordered = sorted(
            ((sparse_term_index(str(term)), float(weight)) for term, weight in values.items()),
            key=lambda item: item[0],
        )
        return {
            "indices": [index for index, _ in ordered],
            "values": [weight for _, weight in ordered],
        }

    @staticmethod
    def _metadata_for(chunk: Chunk) -> dict[str, Any]:
        policy = chunk.access_policy
        metadata: dict[str, Any] = {
            "document_id": chunk.document_id,
            "version": chunk.version,
            "text": chunk.text,
            "section_path": json.dumps(list(chunk.section_path), ensure_ascii=False),
            "page_number": chunk.page_number or 0,
            "source_uri": chunk.source.stable_uri if chunk.source else "",
            "acl_public": policy is None or policy.public,
            "acl_principals": list(policy.principals) if policy else [],
            "acl_groups": list(policy.groups) if policy else [],
            "metadata_json": json.dumps(dict(chunk.metadata), ensure_ascii=False),
            "page_metadata_json": json.dumps(dict(chunk.page_metadata), ensure_ascii=False),
        }
        for key, value in chunk.metadata.items():
            if isinstance(value, (str, int, float, bool)):
                metadata[f"meta_{key}"] = value
        return metadata

    @staticmethod
    def _filter_for(filters: RetrievalFilters | None) -> dict[str, Any] | None:
        if filters is None:
            return None
        clauses: list[dict[str, Any]] = []
        if filters.document_ids:
            clauses.append({"document_id": {"$in": list(filters.document_ids)}})
        for key, value in filters.metadata.items():
            if not isinstance(value, (str, int, float, bool)):
                raise ValueError("Pinecone metadata filters must use scalar values")
            clauses.append({f"meta_{key}": {"$eq": value}})

        acl_options: list[dict[str, Any]] = [{"acl_public": {"$eq": True}}]
        if filters.principal:
            acl_options.append({"acl_principals": {"$in": [filters.principal]}})
        if filters.groups:
            acl_options.append({"acl_groups": {"$in": list(filters.groups)}})
        clauses.append({"$or": acl_options})
        if len(clauses) == 1:
            return clauses[0]
        return {"$and": clauses}

    @classmethod
    def _chunk_from_metadata(cls, chunk_id: str, metadata: Mapping[str, Any]) -> Chunk:
        section_path = cls._json_list(metadata.get("section_path", "[]"))
        page_number = int(metadata.get("page_number", 0) or 0) or None
        source_uri = str(metadata.get("source_uri", ""))
        source = SourceLocation(uri=source_uri) if source_uri else None
        policy = AccessPolicy(
            public=bool(metadata.get("acl_public", False)),
            principals=tuple(metadata.get("acl_principals", ()) or ()),
            groups=tuple(metadata.get("acl_groups", ()) or ()),
        )
        return Chunk(
            chunk_id=chunk_id,
            document_id=str(metadata.get("document_id", "unknown")),
            version=str(metadata.get("version", "unknown")),
            text=str(metadata.get("text", "")),
            section_path=section_path,
            page_number=page_number,
            metadata=cls._json_mapping(metadata.get("metadata_json", "{}")),
            page_metadata=cls._json_mapping(metadata.get("page_metadata_json", "{}")),
            source=source,
            access_policy=policy,
        )

    @staticmethod
    def _json_list(value: Any) -> tuple[str, ...]:
        try:
            parsed = json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            return ()
        return tuple(str(item) for item in (parsed or ()))

    @staticmethod
    def _json_mapping(value: Any) -> dict[str, Any]:
        try:
            parsed = json.loads(value) if isinstance(value, str) else value
        except json.JSONDecodeError:
            return {}
        return dict(parsed or {}) if isinstance(parsed, Mapping) else {}

    @staticmethod
    def _value(value: Any, name: str, default: Any = None) -> Any:
        if isinstance(value, Mapping):
            return value.get(name, default)
        return getattr(value, name, default)

    @classmethod
    def _match_id(cls, match: Any) -> str:
        return str(cls._value(match, "id", ""))

    @classmethod
    def _match_metadata(cls, match: Any) -> Mapping[str, Any]:
        return cls._value(match, "metadata", {}) or {}


__all__ = ["PineconeHybridIndex", "sparse_term_index"]
