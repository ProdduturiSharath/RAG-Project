"""Focused Phase 5 leakage and false-negative guards."""

from __future__ import annotations

from typing import Any

import pytest

from rag_service.domain import Chunk
from rag_service.evaluation.metrics import paired_bootstrap, score_question
from rag_service.evaluation.phase5 import (
    hard_negative_allowed,
    select_unique_passages,
    union_rank_accepts,
    violates_behavior_style,
)
from rag_service.retrieval.bm25 import Bm25Index, bm25_search
from scripts import phase5_prepare


def _manifest() -> tuple[dict[str, str], dict[str, Any]]:
    assignments = {"train-lineage": "train", "dev-lineage": "dev"}
    manifest = {
        "lineages": {
            "train-lineage": {"family_key": "family-train"},
            "dev-lineage": {"family_key": "family-dev"},
        }
    }
    return assignments, manifest


def _record(lineage: str, text: str, kind: str = "text") -> dict[str, object]:
    return {
        "lineage_key": lineage,
        "kind": kind,
        "text": text,
        "metadata": {},
        "content_hash": f"hash-{lineage}",
    }


def test_only_train_families_enter_materialization() -> None:
    assignments, manifest = _manifest()
    train = _record("train-lineage", "PostgreSQL setting details " + "useful guidance " * 30)
    dev = _record("dev-lineage", "PostgreSQL dev text " + "useful guidance " * 30)
    result = select_unique_passages([train, dev], assignments, manifest, ())
    assert [row["lineage_key"] for row in result] == ["train-lineage"]


def test_gold_quote_in_train_passage_is_skipped() -> None:
    assignments, manifest = _manifest()
    record = _record("train-lineage", "A gold phrase " + "details " * 40)
    assert select_unique_passages([record], assignments, manifest, {"A gold phrase details"}) == []


def test_reference_only_stub_is_not_training_text() -> None:
    assignments, manifest = _manifest()
    record = _record("train-lineage", "See another section for details " * 20)
    assert select_unique_passages([record], assignments, manifest, ()) == []


def test_hard_negative_rejects_same_family_and_equal_text() -> None:
    positive = {"text": "same words", "content_hash": "one", "family_key": "family"}
    assert not hard_negative_allowed(
        positive, {"text": "same words", "content_hash": "two", "family_key": "other"}
    )
    assert not hard_negative_allowed(
        positive, {"text": "different", "content_hash": "two", "family_key": "family"}
    )
    assert hard_negative_allowed(
        positive, {"text": "different", "content_hash": "two", "family_key": "other"}
    )


def test_behavior_style_cannot_repeat_identifier() -> None:
    passage = "Set shared_buffers before starting the server; shared_buffers controls memory."
    assert violates_behavior_style("How should shared_buffers be configured?", passage)
    assert violates_behavior_style("How should memory allocation be configured?", passage) is None


def test_union_rank_is_inclusive_and_rejects_rank_201() -> None:
    assert union_rank_accepts("p", ({"p": 200},), 200)
    assert union_rank_accepts("p", ({"p": 201},), 200) is False


def test_extract_json_strips_thinking_trace() -> None:
    assert phase5_prepare.extract_json('<think>private trace</think>{"ok": true}') == {"ok": True}


def test_trial_counts_queries_and_uses_two_word_openings(monkeypatch: pytest.MonkeyPatch) -> None:
    passages = [{"content_hash": f"p-{index}", "text": "x"} for index in range(10)]

    def fake_with_retries(candidate: Any, group: Any, key: str, cache: Any, state: Any) -> Any:
        values = []
        for passage in group:
            index = int(passage["content_hash"].split("-")[1])
            values.append({"content_hash": passage["content_hash"], "queries": [
                {"text": f"opening{index} {style} goal", "style": style,
                 "answerable_from_passage": True}
                for style in phase5_prepare.STYLE_NAMES
            ]})
        return values, 0.01

    monkeypatch.setattr(phase5_prepare, "with_retries", fake_with_retries)
    result = phase5_prepare.trial(
        {"provider": "deepseek", "model": "deepseek-v4-pro"}, passages, "secret"
    )
    assert result["valid_queries"] == 40
    assert result["distinct_openings"] == 40
    assert result["passed"] is True


def test_cached_batches_are_reused_before_balancing_uncached_batches(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any
) -> None:
    monkeypatch.setattr(phase5_prepare, "CACHE", tmp_path)
    candidates = [
        {"provider": "deepseek", "model": "deepseek-v4-pro"},
        {"provider": "deepseek", "model": "deepseek-flash"},
        {"provider": "velona", "model": "qwen/qwen3.7-plus"},
    ]
    groups = [[{"content_hash": f"p-{index}", "text": "passage"}] for index in range(6)]
    cached = phase5_prepare.generation_cache_path(candidates[1], groups[0])
    cached.parent.mkdir(parents=True)
    cached.write_text("cached")
    assigned = [0, 0, 0]

    selections = [
        phase5_prepare.select_generation_candidate(candidates, group, assigned)
        for group in groups
    ]

    assert [phase5_prepare.generator_label(item[0]) for item in selections] == [
        "deepseek/deepseek-flash",
        "deepseek/deepseek-v4-pro",
        "velona/qwen/qwen3.7-plus",
        "deepseek/deepseek-v4-pro",
        "deepseek/deepseek-flash",
        "velona/qwen/qwen3.7-plus",
    ]
    assert [item[3] for item in selections] == [True, False, False, False, False, False]
    assert assigned == [2, 2, 2]


def test_generation_cache_key_keeps_existing_batches_reusable(tmp_path: Any) -> None:
    candidate = {"provider": "deepseek", "model": "deepseek-flash"}
    passages = [{"content_hash": "p-1", "text": "passage"}]
    expected = phase5_prepare.text_hash("deepseek:deepseek-flash:p-1")
    assert phase5_prepare.generation_cache_path(candidate, passages, tmp_path).name == (
        expected + ".json"
    )


def test_failed_batch_recovers_each_passage_and_reports_progress(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    passages = [{"content_hash": f"p-{index}", "text": "passage"} for index in range(3)]
    calls: list[int] = []

    def fake_with_retries(
        candidate: Any, group: list[dict[str, Any]], key: str, cache: Any, state: Any
    ) -> Any:
        calls.append(len(group))
        if len(group) == 3:
            raise RuntimeError("wrong number of passage objects")
        return (
            [
                {
                    "content_hash": group[0]["content_hash"],
                    "queries": [
                        {
                            "text": f"query {style}",
                            "style": style,
                            "answerable_from_passage": True,
                        }
                        for style in phase5_prepare.STYLE_NAMES
                    ],
                }
            ],
            0.1,
        )

    monkeypatch.setattr(phase5_prepare, "with_retries", fake_with_retries)
    values, latency = phase5_prepare.generate_group(
        {"provider": "deepseek", "model": "deepseek-v4-pro"},
        passages,
        "secret",
        tmp_path / "group.json",
        {},
        batch_number=1,
        total_batches=10,
    )
    assert len(values) == 3
    assert latency == pytest.approx(0.3)
    assert calls == [3, 1, 1, 1]
    assert (tmp_path / "group.json").exists()
    assert "Recovering deepseek/deepseek-v4-pro batch 1/10" in capsys.readouterr().out


def test_bm25_index_matches_one_shot_search() -> None:
    chunks = [
        Chunk("a", "doc", "v1", "alpha beta"),
        Chunk("b", "doc", "v1", "alpha alpha gamma"),
        Chunk("c", "doc", "v1", "unrelated"),
    ]
    assert Bm25Index(chunks).search("alpha", 3) == bm25_search("alpha", chunks, 3)


def test_boundary_window_and_sibling_family_diagnostics() -> None:
    row = {
        "id": "boundary",
        "type": "factoid",
        "lineage_key": "family#gold",
        "version_independent": False,
        "target_version": "v1",
        "gold_versions": ["v1"],
        "acl_allowance": True,
        "evidence_spans": [{"quote": "alpha beta gamma", "lineage_key": "family#gold"}],
    }
    ranked = [
        {
            "chunk_id": "2", "text": "gamma", "version": "v1",
            "lineage_key": "family#sibling", "ordinal": 2,
        },
        {
            "chunk_id": "1", "text": "alpha beta", "version": "v1",
            "lineage_key": "family#sibling", "ordinal": 1,
        },
    ]
    scores = score_question(row, ranked, relevant_count=2)
    assert scores["windowed_recall@5"] == 1.0
    assert scores["section_family_recall@5"] == 1.0


def test_paired_bootstrap_uses_one_mean_row_per_question() -> None:
    from scripts.phase5_eval import aggregate_seed_rows

    left = aggregate_seed_rows([
        {"id": "q1", "lineage_key": "l1", "seed": 1, "metrics": {"m": 0.2}},
        {"id": "q1", "lineage_key": "l1", "seed": 2, "metrics": {"m": 0.4}},
        {"id": "q2", "lineage_key": "l2", "seed": 1, "metrics": {"m": 0.6}},
        {"id": "q2", "lineage_key": "l2", "seed": 2, "metrics": {"m": 0.8}},
    ])
    right = [{**row, "metrics": {"m": 0.1}} for row in left]
    assert [row["id"] for row in left] == ["q1", "q2"]
    assert paired_bootstrap(left, right, "m", samples=100)["mean"] == pytest.approx(0.4)
