import math
from typing import Any

import pytest

from rag_service.evaluation.metrics import (
    bootstrap,
    covers,
    guard_nonzero_scores,
    ndcg,
    paired_bootstrap,
    score_question,
    version_confusion,
)


def question(**overrides: Any) -> dict[str, Any]:
    return {"id": "q", "type": "version_specific", "lineage_key": "setting",
            "version_independent": False, "target_version": "pg-17", "acl_allowance": True,
            "gold_versions": ["pg-16", "pg-17"],
            "evidence_spans": [{"quote": "default is 20", "lineage_key": "setting"}],
            **overrides}


def chunk(text: str = "The default\n is   20 today.", version: str = "pg-17",
          lineage: str = "setting") -> dict[str, Any]:
    return {"text": text, "version": version, "lineage_key": lineage}


def test_hit_requires_whole_normalized_quote_and_appropriate_version() -> None:
    row = question()
    assert covers(row, chunk()) == {0}
    assert not covers(row, chunk(version="pg-16"))
    assert not covers(row, chunk(text="default is"))
    assert not covers(row, chunk(text="Default is 20"))
    independent = question(type="factoid", version_independent=True)
    assert covers(independent, chunk(version="pg-16")) == {0}
    assert not covers(independent, chunk(version="pg-15"))
    assert not covers(question(version_independent=True), chunk(version="pg-16"))
    assert covers(row, chunk(lineage="equivalent-elsewhere")) == {0}


def test_multi_hop_coverage_is_distinct_from_all_quotes_and_deduplicates_quotes() -> None:
    row = question(type="multi_hop", evidence_spans=[{"quote": "default is 20"},
                                                   {"quote": "read with current_setting"}])
    ranked = [chunk(), chunk(), chunk("read with\ncurrent_setting")]
    scores = score_question(row, ranked, relevant_count=3)
    assert scores["recall@1"] == 0.5
    assert scores["all_quotes@1"] == 0
    assert scores["recall@3"] == scores["all_quotes@3"] == 1
    assert score_question(row, [], 3)["mrr"] == 0
    assert score_question(question(type="unanswerable"), ranked, 0) == {}
    assert score_question(question(type="acl", acl_allowance=False), ranked, 3) == {}


def test_version_confusion_requires_same_lineage_and_rank_above_first_correct() -> None:
    row = question()
    wrong = chunk(text="default is 10", version="pg-16")
    unrelated = chunk(version="pg-15", lineage="other")
    assert version_confusion(row, [wrong, chunk(), wrong], 1) == 1
    assert version_confusion(row, [chunk(), wrong], 10) == 0
    assert version_confusion(row, [unrelated, wrong], 1) == 0
    assert version_confusion(row, [unrelated, wrong], 3) == 1  # Correct never returned
    assert version_confusion(row, [unrelated], 10) == 0


def test_ndcg_uses_full_ideal_not_just_retrieved_hits() -> None:
    assert ndcg([1, 1], [1, 1]) == 1
    assert ndcg([0, 1], [1]) == pytest.approx(1 / math.log2(3))
    assert ndcg([1], [1, 1]) == pytest.approx(1 / (1 + 1 / math.log2(3)))
    assert ndcg([0, 0], [1]) == 0
    assert ndcg([], []) == 0
    assert ndcg([0] * 10 + [1], [1]) == 0


def test_score_deduplicates_equivalent_version_evidence_for_recall_and_ndcg() -> None:
    row = question(type="factoid", version_independent=True,
                   gold_versions=["pg-16", "pg-17"])
    ranked = [chunk(version="pg-16"), chunk(version="pg-17")]
    scores = score_question(row, ranked, relevant_count=2)
    assert scores["recall@1"] == scores["recall@10"] == 1
    assert scores["mrr"] == 1
    assert scores["ndcg@10"] == 1


def test_zero_score_guard_fails_loudly_for_a_dead_arm() -> None:
    rows = [{"metrics": {"recall@10": 0.0}} for _ in range(3)]
    with pytest.raises(RuntimeError, match="exactly zero"):
        guard_nonzero_scores(rows, system="sparse-postgres")
    guard_nonzero_scores([{"metrics": {"recall@10": 0.1}}], system="healthy")


def test_bootstrap_is_deterministic_clustered_and_paired_by_id() -> None:
    values, keys = [0.0, 1.0, 1.0, 1.0], ["paired", "paired", "single-a", "single-b"]
    result = bootstrap(values, keys, seed=7, samples=1000)
    assert result == bootstrap(values[::-1], keys[::-1], seed=7, samples=1000)
    assert result["mean"] == 0.75
    assert result["lineages"] == 3
    # A paired lineage's two questions are never separated, so its mean stays 0.5.
    assert bootstrap([0, 1], ["pair", "pair"])["ci95"] == [0.5, 0.5]
    rows: list[dict[str, Any]] = [{"id": str(i), "lineage_key": key, "metrics": {"m": value}}
            for i, (key, value) in enumerate(zip(keys, values, strict=True))]
    same = paired_bootstrap(rows, rows[::-1], "m", seed=7)
    assert same["ci95"] == [0, 0] and same["within_noise"] is True
    better = [{**row, "metrics": {"m": row["metrics"]["m"] + 0.25}} for row in rows]
    difference = paired_bootstrap(better, rows, "m", seed=7)
    assert difference["mean"] == 0.25 and difference["within_noise"] is False
    with pytest.raises(ValueError, match="identical question IDs"):
        paired_bootstrap(rows, rows[:-1], "m")
