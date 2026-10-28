"""Hypothesis ACL properties shared by in-memory and PostgreSQL adapters."""

from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from rag_service.domain import AccessPolicy, Chunk, DocumentSection
from rag_service.ingestion import DeterministicChunker
from rag_service.retrieval import (
    Bm25SparseEncoder,
    HashEmbeddingEncoder,
    InMemoryHybridIndex,
    PostgresHybridIndex,
    RetrievalFilters,
)
from rag_service.storage import PostgresVersionedStore

principals = st.lists(st.sampled_from(["alice", "bob", "carol"]), unique=True, max_size=3)
groups = st.lists(st.sampled_from(["sre", "docs", "finance"]), unique=True, max_size=3)
versions = st.sampled_from(["pg-15", "pg-16", "pg-17"])


def policy(public: bool, allowed_principals: list[str], allowed_groups: list[str]) -> AccessPolicy:
    return AccessPolicy(
        public=public, principals=tuple(allowed_principals), groups=tuple(allowed_groups)
    )


def _memory_index(
    access_policy: AccessPolicy, version: str
) -> tuple[InMemoryHybridIndex, tuple[float, ...]]:
    index = InMemoryHybridIndex()
    index.upsert(
        [
            Chunk(
                "c", "doc", version, "authorization property evidence", access_policy=access_policy
            )
        ],
        dense_vectors=[(1.0,)],
        sparse_vectors=[{}],
    )
    return index, (1.0,)


def _postgres_index(
    access_policy: AccessPolicy, version: str
) -> tuple[PostgresHybridIndex, tuple[float, ...], str]:
    database_url = (
        os.getenv("RAG_TEST_DATABASE_URL")
        or os.getenv("RAG_EVAL_DATABASE_URL")
        or os.getenv("RAG_DATABASE_URL")
    )
    if not database_url:
        pytest.skip("RAG_TEST_DATABASE_URL is not provisioned")
    document_id = "phase7-hypothesis-" + uuid4().hex
    embedder = HashEmbeddingEncoder(dimensions=8)
    sparse = Bm25SparseEncoder()
    store = PostgresVersionedStore(
        database_url,
        DeterministicChunker(max_tokens=20, overlap_tokens=0),
        embedder=embedder,
        sparse_encoder=sparse,
        migrations_path="migrations",
    )
    store.migrate()
    store.ingest(
        document_id,
        [DocumentSection(text="authorization property evidence")],
        version,
        access_policy=access_policy,
    )
    vector = tuple(
        float(value) for value in embedder.embed(("authorization property evidence",))[0]
    )
    return PostgresHybridIndex(database_url, migrations_path="migrations"), vector, document_id


@pytest.mark.parametrize("adapter_kind", ["memory", "postgres"])
@settings(max_examples=8, deadline=None)
@given(
    public=st.booleans(),
    allowed_principals=principals,
    allowed_groups=groups,
    principal=st.one_of(st.none(), st.sampled_from(["alice", "bob", "carol"])),
    caller_groups=groups,
    version=versions,
)
def test_authorization_soundness(
    adapter_kind: str,
    public: bool,
    allowed_principals: list[str],
    allowed_groups: list[str],
    principal: str | None,
    caller_groups: list[str],
    version: str,
) -> None:
    access_policy = policy(public, allowed_principals, allowed_groups)
    index: Any
    if adapter_kind == "memory":
        index, vector = _memory_index(access_policy, version)
        matches: Any = index.search(
            vector,
            {},
            top_k=5,
            alpha=1.0,
            filters=RetrievalFilters(principal=principal, groups=tuple(caller_groups)),
        )
    else:
        index, vector, document_id = _postgres_index(access_policy, version)
        matches = index.search(
            vector,
            {},
            top_k=5,
            alpha=1.0,
            filters=RetrievalFilters(
                document_ids=(document_id,), principal=principal, groups=tuple(caller_groups)
            ),
        )
    assert all(
        match.chunk.access_policy is None
        or match.chunk.access_policy.allows(principal, groups=caller_groups)
        for match in matches
    )
    expected = access_policy.allows(principal, groups=caller_groups)
    assert bool(matches) is expected


@pytest.mark.parametrize("adapter_kind", ["memory", "postgres"])
@settings(max_examples=8, deadline=None)
@given(
    public=st.booleans(),
    allowed_principals=principals,
    allowed_groups=groups,
    principal=st.one_of(st.none(), st.sampled_from(["alice", "bob", "carol"])),
    group_set=groups,
    extra_groups=groups,
    version=versions,
)
def test_group_subset_monotonicity(
    adapter_kind: str,
    public: bool,
    allowed_principals: list[str],
    allowed_groups: list[str],
    principal: str | None,
    group_set: list[str],
    extra_groups: list[str],
    version: str,
) -> None:
    smaller = set(group_set)
    larger = smaller | set(extra_groups)
    access_policy = policy(public, allowed_principals, allowed_groups)
    index: Any
    if adapter_kind == "memory":
        index, vector = _memory_index(access_policy, version)
        first = index.search(
            vector,
            {},
            top_k=5,
            alpha=1.0,
            filters=RetrievalFilters(principal=principal, groups=tuple(sorted(smaller))),
        )
        second = index.search(
            vector,
            {},
            top_k=5,
            alpha=1.0,
            filters=RetrievalFilters(principal=principal, groups=tuple(sorted(larger))),
        )
    else:
        index, vector, document_id = _postgres_index(access_policy, version)
        first = index.search(
            vector,
            {},
            top_k=5,
            alpha=1.0,
            filters=RetrievalFilters(
                document_ids=(document_id,), principal=principal, groups=tuple(sorted(smaller))
            ),
        )
        second = index.search(
            vector,
            {},
            top_k=5,
            alpha=1.0,
            filters=RetrievalFilters(
                document_ids=(document_id,), principal=principal, groups=tuple(sorted(larger))
            ),
        )
    assert {match.chunk.chunk_id for match in first} <= {match.chunk.chunk_id for match in second}


@pytest.mark.parametrize("adapter_kind", ["memory", "postgres"])
@settings(max_examples=8, deadline=None)
@given(
    public=st.booleans(),
    allowed_principals=principals,
    allowed_groups=groups,
    principal=st.sampled_from(["alice", "bob", "carol"]),
    caller_groups=groups,
    version=versions,
)
def test_revocation_and_deletion_are_immediate(
    adapter_kind: str,
    public: bool,
    allowed_principals: list[str],
    allowed_groups: list[str],
    principal: str,
    caller_groups: list[str],
    version: str,
) -> None:
    access_policy = policy(public, allowed_principals, allowed_groups)
    filters = RetrievalFilters(principal=principal, groups=tuple(caller_groups))
    index: Any
    if adapter_kind == "memory":
        index, vector = _memory_index(access_policy, version)
        index.upsert(
            [
                Chunk(
                    "c",
                    "doc",
                    version,
                    "authorization property evidence",
                    access_policy=AccessPolicy(),
                )
            ],
            dense_vectors=[(1.0,)],
            sparse_vectors=[{}],
        )
        revoked = index.search(vector, {}, top_k=5, alpha=1.0, filters=filters)
        index.delete_document("doc", version)
        deleted = index.search(vector, {}, top_k=5, alpha=1.0, filters=filters)
    else:
        database_url = (
            os.getenv("RAG_TEST_DATABASE_URL")
            or os.getenv("RAG_EVAL_DATABASE_URL")
            or os.getenv("RAG_DATABASE_URL")
        )
        if not database_url:
            pytest.skip("RAG_TEST_DATABASE_URL is not provisioned")
        document_id = "phase7-revoke-" + uuid4().hex
        embedder = HashEmbeddingEncoder(dimensions=8)
        sparse = Bm25SparseEncoder()
        store = PostgresVersionedStore(
            database_url,
            DeterministicChunker(max_tokens=20, overlap_tokens=0),
            embedder=embedder,
            sparse_encoder=sparse,
            migrations_path="migrations",
        )
        store.migrate()
        store.ingest(
            document_id,
            [DocumentSection(text="authorization property evidence")],
            version,
            access_policy=access_policy,
        )
        index = PostgresHybridIndex(database_url, migrations_path="migrations")
        postgres_filters = RetrievalFilters(
            document_ids=(document_id,), principal=principal, groups=tuple(caller_groups)
        )
        vector = embedder.embed(("authorization property evidence",))[0]
        # Replacing the ACL with an empty private policy revokes access before deletion.
        store.ingest(
            document_id,
            [DocumentSection(text="authorization property evidence")],
            version,
            access_policy=AccessPolicy(),
        )
        revoked = index.search(vector, {}, top_k=5, alpha=1.0, filters=postgres_filters)
        store.delete_document(document_id, version)
        deleted = index.search(vector, {}, top_k=5, alpha=1.0, filters=postgres_filters)
    assert revoked == ()
    assert deleted == ()
