"""Focused Phase 5 leakage and false-negative guards."""

from __future__ import annotations

import pytest

from rag_service.evaluation.phase5 import (
    hard_negative_allowed,
    select_unique_passages,
    union_rank_accepts,
    violates_behavior_style,
)


def _manifest() -> tuple[dict[str, str], dict[str, object]]:
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


def test_gold_quote_in_train_passage_aborts() -> None:
    assignments, manifest = _manifest()
    record = _record("train-lineage", "A gold phrase " + "details " * 40)
    with pytest.raises(ValueError, match="gold evidence quote"):
        select_unique_passages([record], assignments, manifest, {"A gold phrase details"})


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
