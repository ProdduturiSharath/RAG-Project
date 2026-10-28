"""Equivalence tests for Phase 5 ranking caches and vectorized scoring."""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from collections.abc import Iterator
from dataclasses import replace
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest

import scripts.phase5_eval as evaluator
from rag_service.domain import Chunk
from rag_service.evaluation.metrics import score_question
from rag_service.retrieval.bm25 import clear_bm25_index_cache
from rag_service.retrieval.encoders import tokenize
from scripts.phase5_eval import (
    build_dense_matrix,
    chunk_records,
    clear_phase5_rank_caches,
    rank_bm25,
    rank_dense,
    rank_hybrid,
    resolve_eval_scope,
)


@pytest.fixture(autouse=True)
def clean_caches() -> Iterator[None]:
    clear_bm25_index_cache()
    clear_phase5_rank_caches()
    yield
    clear_bm25_index_cache()
    clear_phase5_rank_caches()


def _chunks() -> list[Chunk]:
    return [
        Chunk("a", "manual", "pg16", "alpha beta", section_path=("public",), ordinal=1,
              content_hash="hash-a", lineage_key="family-a#pg16"),
        Chunk("b", "manual", "pg16", "alpha alpha gamma", section_path=("security",), ordinal=2,
              content_hash="hash-b", lineage_key="family-b#pg16"),
        Chunk("c", "manual", "pg17", "alpha delta", section_path=("public",), ordinal=1,
              content_hash="hash-c", lineage_key="family-a#pg17"),
        Chunk("d", "manual", "pg17", "unrelated", section_path=("public",), ordinal=2,
              content_hash="hash-d", lineage_key="family-c#pg17"),
    ]


def _vectors() -> dict[str, np.ndarray]:
    return {
        "hash-a": np.asarray([1.0, 0.0], dtype=np.float32),
        "hash-b": np.asarray([0.8, 0.2], dtype=np.float32),
        "hash-c": np.asarray([0.0, 1.0], dtype=np.float32),
        "hash-d": np.asarray([0.1, 0.1], dtype=np.float32),
    }


def _reference_dense(
    query: np.ndarray, records: list[dict], vectors: dict[str, np.ndarray], top_k: int
) -> list[dict[str, Any]]:
    # The ORIGINAL implementation: no dependency on the optimized hash lookup.
    scored = []
    for record in records:
        vector = vectors.get(record["content_hash"])
        if vector is None:
            vector = vectors.get(hashlib.sha256(record["text"].encode()).hexdigest())
        if vector is not None and len(vector) == len(query):
            scored.append((float(np.dot(query, vector)), record))
    return [
        dict(record, score=score)
        for score, record in sorted(
            scored, key=lambda value: (-value[0], value[1]["chunk_id"])
        )[:top_k]
    ]


def _reference_bm25(
    query: str, chunks: list[Chunk], records: list[dict], top_k: int
) -> list[dict[str, Any]]:
    token_counts = [Counter(tokenize(chunk.text)) for chunk in chunks]
    document_count = len(token_counts)
    if not document_count or top_k <= 0:
        return []
    average_length = sum(sum(counts.values()) for counts in token_counts) / document_count or 1.0
    document_frequency: Counter[str] = Counter()
    for counts in token_counts:
        document_frequency.update(counts.keys())
    idf = {
        term: math.log(1 + (document_count - frequency + 0.5) / (frequency + 0.5))
        for term, frequency in document_frequency.items()
    }
    scored = []
    for chunk, counts in zip(chunks, token_counts, strict=True):
        length = sum(counts.values())
        score = sum(
            idf[term] * counts[term] * 2.2
            / (counts[term] + 1.2 * (0.25 + 0.75 * length / average_length))
            for term in set(tokenize(query))
            if counts[term]
        )
        if score > 0:
            scored.append((score, chunk.chunk_id))
    by_id = {record["chunk_id"]: record for record in records}
    return [
        dict(by_id[chunk_id], score=score)
        for score, chunk_id in sorted(scored, key=lambda value: (-value[0], value[1]))[:top_k]
    ]


def _reference_hybrid(
    query: str,
    query_vector: np.ndarray,
    chunks: list[Chunk],
    records: list[dict],
    vectors: dict[str, np.ndarray],
    alpha: float,
) -> list[dict[str, Any]]:
    dense = _reference_dense(query_vector, records, vectors, 200)
    sparse = _reference_bm25(query, chunks, records, 200)
    dense_scores = {row["chunk_id"]: max(0.0, row["score"]) for row in dense}
    sparse_scores = {row["chunk_id"]: row["score"] for row in sparse}
    dense_max = max(dense_scores.values(), default=0.0) or 1.0
    sparse_max = max(sparse_scores.values(), default=0.0) or 1.0
    scored = []
    for record in records:
        dense_part = dense_scores.get(record["chunk_id"], 0.0) / dense_max
        sparse_part = sparse_scores.get(record["chunk_id"], 0.0) / sparse_max
        score = alpha * dense_part + (1.0 - alpha) * sparse_part
        scored.append((score, record))
    return [
        dict(record, score=score)
        for score, record in sorted(
            scored, key=lambda value: (-value[0], value[1]["chunk_id"])
        )[:30]
    ]


def _assert_rankings_equal(actual: list[dict], expected: list[dict]) -> None:
    assert [row["chunk_id"] for row in actual] == [row["chunk_id"] for row in expected]
    np.testing.assert_allclose(
        [row["score"] for row in actual], [row["score"] for row in expected], rtol=1e-6, atol=1e-6
    )


def test_vectorized_dense_matches_reference_and_precomputed_fallback_hash() -> None:
    chunks = _chunks()
    chunks[0] = Chunk("a", "manual", "pg16", "alpha beta", content_hash=None, ordinal=1)
    records = chunk_records(chunks)
    fallback_key = hashlib.sha256(b"alpha beta").hexdigest()
    vectors = _vectors() | {fallback_key: _vectors()["hash-a"]}
    query = np.asarray([0.9, 0.1], dtype=np.float32)

    actual = rank_dense(
        query, records, vectors, top_k=3, dense_matrix=build_dense_matrix(records, vectors)
    )
    expected = _reference_dense(query, records, vectors, 3)

    _assert_rankings_equal(actual, expected)
    assert records[0]["fallback_hash"] == fallback_key


def test_cached_bm25_matches_reference_and_reuses_exact_ordered_subset() -> None:
    chunks = _chunks()
    records = chunk_records(chunks)
    clear_bm25_index_cache()
    clear_phase5_rank_caches()

    actual = rank_bm25("alpha", chunks, records, top_k=3)
    expected = _reference_bm25("alpha", chunks, records, 3)
    _assert_rankings_equal(actual, expected)

    from rag_service.retrieval.bm25 import cached_bm25_index

    assert cached_bm25_index(chunks) is cached_bm25_index(chunks)
    assert cached_bm25_index(chunks) is not cached_bm25_index(list(reversed(chunks)))


def test_hybrid_equivalence_survives_acl_and_version_scoped_subsets() -> None:
    chunks = _chunks()
    records = chunk_records(chunks)
    vectors = _vectors()
    query = np.asarray([0.9, 0.1], dtype=np.float32)

    # Simulate the strict ACL-filtered candidate set: the restricted security
    # chunk is excluded before either sparse or dense ranking.
    acl_chunks = [chunk for chunk in chunks if chunk.section_path != ("security",)]
    acl_records = [record for record in records if record["chunk_id"] != "b"]
    actual_acl = rank_dense(query, acl_records, vectors, top_k=3)
    expected_acl = _reference_dense(query, acl_records, vectors, 3)
    _assert_rankings_equal(actual_acl, expected_acl)

    # Automatic version scope must be applied before ranking and must preserve
    # the same hybrid ordering as the reference implementation.
    scoped_records, scope = resolve_eval_scope(
        "How does PostgreSQL 17 behave?", records, enabled=True
    )
    assert scope.filters.product_version == "pg17"
    scoped_ids = {record["chunk_id"] for record in scoped_records}
    scoped_chunks = [chunk for chunk in acl_chunks if chunk.chunk_id in scoped_ids]
    scoped_records = [record for record in acl_records if record["chunk_id"] in scoped_ids]
    actual = rank_hybrid(
        "alpha", query, scoped_chunks, scoped_records, vectors, alpha=0.25
    )
    expected = _reference_hybrid("alpha", query, scoped_chunks, scoped_records, vectors, 0.25)
    _assert_rankings_equal(actual, expected)

    metric_row = {
        "id": "q1",
        "type": "factoid",
        "version_independent": False,
        "target_version": "pg17",
        "gold_versions": ["pg17"],
        "lineage_key": "family-a",
        "evidence_spans": [{"quote": "alpha delta", "lineage_key": "family-a"}],
    }
    assert score_question(metric_row, actual, 1) == score_question(metric_row, expected, 1)


def test_missing_content_hash_key_still_falls_back_without_hashing_in_rank(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    records = chunk_records(_chunks())
    vectors = {records[0]["fallback_hash"]: np.array([1, 0], dtype=np.float32)}
    query = np.array([1, 0], dtype=np.float32)
    expected = _reference_dense(query, records, vectors, 30)
    monkeypatch.setattr(evaluator.hashlib, "sha256", MagicMock(side_effect=AssertionError))
    actual = rank_dense(query, records, vectors)
    _assert_rankings_equal(actual, expected)
    assert [row["chunk_id"] for row in actual] == ["a"]


@pytest.mark.parametrize("top_k", [0, 1, 7, 30, 200, 700])
def test_dense_cutoff_ties_and_zero_scores_match_full_sort(top_k: int) -> None:
    chunks = [Chunk(f"{i:04}", "manual", "pg17", "alpha", content_hash=f"h{i}")
              for i in reversed(range(600))]
    records = chunk_records(chunks)
    vectors = {f"h{i}": np.array([i % 4, 0], dtype=np.float32) for i in range(600)}
    matrix = build_dense_matrix(records, vectors)
    for query in (np.array([1, 0], dtype=np.float32), np.zeros(2, dtype=np.float32)):
        _assert_rankings_equal(
            rank_dense(query, records, vectors, top_k, matrix),
            _reference_dense(query, records, vectors, top_k),
        )


def test_dense_caches_do_not_cross_models_queries_or_subsets() -> None:
    records = chunk_records(_chunks())
    vectors = _vectors() | {"hash-d": np.array([1, 2, 3], dtype=np.float32)}
    for values in (vectors, {key: -value for key, value in vectors.items()}):
        matrix = build_dense_matrix(records, values)
        for subset in (records, records[1:], records[::-1], []):
            for query in (np.array([1, 0], dtype=np.float32),
                          np.array([0, 1], dtype=np.float32),
                          np.ones(3, dtype=np.float32)):
                _assert_rankings_equal(
                    rank_dense(query, subset, values, 30, matrix),
                    _reference_dense(query, subset, values, 30),
                )


def test_sparse_cache_reuses_scores_not_stale_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    chunks = _chunks()
    records = chunk_records(chunks)
    first = rank_bm25("alpha", chunks, records, 3)
    search = MagicMock(side_effect=AssertionError("must reuse sparse scores"))
    with monkeypatch.context() as patch:
        patch.setattr(evaluator.Bm25Index, "search", search)
        changed_records = [{**record, "section_family": "updated"} for record in records]
        again = rank_bm25("alpha", chunks, changed_records, 3)
        assert all(record["section_family"] == "updated" for record in again)
        _assert_rankings_equal(again, first)
    # Reusing ids for a new revision must invalidate both index and score cache.
    revised = [replace(chunks[0], text="omega"), *chunks[1:]]
    _assert_rankings_equal(
        rank_bm25("alpha", revised, chunk_records(revised), 3),
        _reference_bm25("alpha", revised, chunk_records(revised), 3),
    )
    for subset in (chunks[::-1], chunks[1:], []):
        for top_k in (0, 1, 3):
            subset_records = chunk_records(subset)
            _assert_rankings_equal(
                rank_bm25("alpha", subset, subset_records, top_k),
                _reference_bm25("alpha", subset, subset_records, top_k),
            )


@pytest.mark.parametrize("alpha", [0.0, 0.25, 0.5, 0.75, 1.0])
def test_hybrid_zero_fill_is_sorted_and_matches_reference(alpha: float) -> None:
    chunks = [Chunk(f"{i:03}", "manual", "pg17", "omega", content_hash=f"h{i}")
              for i in reversed(range(80))]
    records = chunk_records(chunks)
    vectors = {"h1": np.array([1, 0], dtype=np.float32)}
    query = np.array([1, 0], dtype=np.float32)
    _assert_rankings_equal(
        rank_hybrid("unknown", query, chunks, records, vectors, alpha),
        _reference_hybrid("unknown", query, chunks, records, vectors, alpha),
    )


@pytest.mark.parametrize("name,alpha,scoped", [
    ("dense", None, False), ("bm25", None, False),
    ("hybrid", 0.5, False), ("recommended", 0.25, True),
])
def test_evaluate_arm_exact_metrics_acl_scope_and_warm_cache(
    name: str, alpha: float | None, scoped: bool,
) -> None:
    chunks = _chunks()
    records = chunk_records(chunks)
    vectors = _vectors()
    query = np.array([0.75, 0.25], dtype=np.float32)
    matrix = build_dense_matrix(records, vectors)
    policy = {
        "principals": [{"id": "guest", "groups": []}, {"id": "admin", "groups": ["sre"]}],
        "restricted_section_titles": ["security"], "restricted_allowed_groups": ["sre"],
    }
    # Reuse a question id with changed requester, scope question, and evidence:
    # none of those may reuse another query's filtered set or relevant records.
    for requester, version in [("admin", "pg16"), ("guest", "pg17"), ("guest", "pg16")]:
        row: dict[str, Any] = {
            "id": "same-id", "type": "acl", "requester": requester, "acl_allowance": True,
            "question": f"PostgreSQL {version[2:]} alpha", "lineage_key": "family-a",
            "version_independent": False, "target_version": version, "gold_versions": [version],
            "evidence_spans": [{"quote": "alpha", "lineage_key": "family-a"}],
        }
        authorized = [chunk for chunk in chunks if evaluator.allowed(chunk, policy, requester)]
        authorized_ids = {chunk.chunk_id for chunk in authorized}
        accessible = [record for record in records if record["chunk_id"] in authorized_ids]
        selected, scope = resolve_eval_scope(row["question"], accessible, enabled=scoped)
        selected_ids = {record["chunk_id"] for record in selected}
        selected_chunks = [chunk for chunk in authorized if chunk.chunk_id in selected_ids]
        if name == "bm25":
            expected = _reference_bm25(row["question"], selected_chunks, selected, 30)
        elif alpha is None:
            expected = _reference_dense(query, selected, vectors, 30)
        else:
            expected = _reference_hybrid(
                row["question"], query, selected_chunks, selected, vectors, alpha
            )
        relevant = [record for record in accessible if evaluator.covers(row, record)]
        metrics = score_question(
            row, expected, len(relevant), relevant=relevant,
            scope=scope.filters if scope else evaluator.RetrievalFilters(),
        )
        for _warm in range(2):
            actual = evaluator.evaluate_arm(
                name, {"same-id": query}, vectors, chunks, records, [row],
                alpha=alpha, recommended=scoped, policy=policy, dense_matrix=matrix,
            )[0]
            _assert_rankings_equal(actual["retrieved"], expected)
            assert actual["metrics"] == metrics
            assert actual["relevant_chunk_count"] == len(relevant)
            assert actual["leakage_count"] == 0
            if requester == "guest":
                assert "b" not in [record["chunk_id"] for record in actual["retrieved"]]
            if scoped:
                assert {record["version"] for record in actual["retrieved"]} <= {version}


@pytest.mark.parametrize("count,skip", [(2, True), (1, False), (0, False)])
def test_import_vectors_reuses_only_complete_counts(count: int, skip: bool) -> None:
    connection = MagicMock()
    connection.execute.return_value.fetchone.return_value = {"count": count}
    evaluator.import_vectors(connection, "phase5_existing", "arm", {
        "a": np.array([1, 0], dtype=np.float32), "b": np.array([0, 1], dtype=np.float32),
    })
    assert connection.cursor.called is not skip
    connection.commit.assert_called_once()
    args = connection.execute.call_args
    assert args.args[1] == ("arm",)
    if not skip:
        connection.cursor.return_value.__enter__.return_value.executemany.assert_called_once()
