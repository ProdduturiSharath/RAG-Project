"""Cache isolation, dev/test integrity and metrics on user-visible failure cases."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import httpx
import pytest

from rag_service.evaluation.phase6 import (
    EvaluationCache,
    answer_metrics,
    calibrate,
    freeze_subset,
    summarize,
    token_cost,
)
from rag_service.generation.models import Claim
from rag_service.generation.openai_compatible import OpenAICompatibleGenerator
from rag_service.generation.verification import abstention, verify_answer
from tests.unit.test_phase6_generation import answer, request, sse_response


def row(*, split: str = "dev", answerable: bool = True) -> dict[str, Any]:
    return {
        "id": "q",
        "split": split,
        "type": "factoid",
        "answerability": answerable,
        "acl_allowance": True,
        "target_version": "pg-16",
        "expected_answer": "8",
        "lineage_key": "family",
    }


async def test_cache_reuse_and_context_question_id_prompt_invalidation(tmp_path: Path) -> None:
    count = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal count
        count += 1
        return sse_response()

    generator = OpenAICompatibleGenerator(
        api_key="test-only", verified=False, min_interval=0, transport=httpx.MockTransport(handler)
    )
    cache = EvaluationCache(tmp_path)
    first, hit = await cache.generate(generator, request(), "q1")
    assert not hit
    second, hit = await cache.generate(generator, request(), "q1")
    assert hit and first == second and count == 1
    assert second.metadata["cost"]["billed_usd"] is None
    identity = cache.identity(generator, request(), "q1")
    assert cache.identity(generator, request(), "q2") != identity
    assert cache.identity(generator, replace(request(), query="changed"), "q1") != identity
    changed = replace(request().matches[0].chunk, text="new context")
    req = replace(request(), matches=(replace(request().matches[0], chunk=changed),))
    assert cache.identity(generator, req, "q1") != identity
    # Serving's generator has no cache option or import; generation never reads this entry.
    await generator.generate(request())
    assert count == 2


async def test_errors_and_truncation_never_cached(tmp_path: Path) -> None:
    generator = OpenAICompatibleGenerator(
        api_key="test-only",
        verified=False,
        transport=httpx.MockTransport(lambda req: sse_response(finish="length")),
    )
    cache = EvaluationCache(tmp_path)
    with pytest.raises(ValueError):
        await cache.generate(generator, request(), "q1")
    assert not list(tmp_path.rglob("*.json"))
    generator.transport = httpx.MockTransport(lambda req: httpx.Response(401))
    with pytest.raises(RuntimeError):
        await cache.generate(generator, request(), "q1")
    assert not list(tmp_path.rglob("*.json"))


def test_subset_frozen_complete_and_no_test_calibration(tmp_path: Path) -> None:
    rows = [json.loads(line) for line in Path("data/eval/gold.jsonl").read_text().splitlines()]
    path = tmp_path / "subset.json"
    manifest = freeze_subset(rows, path)
    assert len(manifest["ids"]) == 60
    chosen = [r for r in rows if r["id"] in manifest["ids"]]
    assert all(r["split"] == "test" for r in chosen)
    assert sum(not r["answerability"] for r in chosen) == 12
    assert sum(r["review_method"] == "human" for r in chosen) == 2
    assert {r["type"] for r in chosen} == {r["type"] for r in rows}
    assert freeze_subset(rows, path) == manifest
    with pytest.raises(ValueError, match="dev only"):
        calibrate([(row(split="test"), request(), answer())])


def test_calibration_and_metrics_handle_abstention_wrong_version_and_unsupported() -> None:
    good = answer_metrics(answer(), request(), row())
    assert good == {
        "correctness": 1,
        "faithfulness": 1,
        "citation_precision": 1,
        "abstention_correctness": 1,
        "wrong_version_answers": 0,
    }
    noanswer = answer_metrics(abstention(), request(), row(answerable=False))
    assert noanswer["correctness"] == 1 and noanswer["faithfulness"] is None
    assert answer_metrics(abstention(), request(), row())["correctness"] == 0
    wrong = replace(answer(), answered_version="pg-17")
    assert answer_metrics(wrong, request(), row())["wrong_version_answers"] == 1
    assert answer_metrics(wrong, request(), row())["correctness"] == 0
    weak = replace(request(), query="missing_identifier")
    calibration = calibrate([(row(), request(), answer()), (row(answerable=False), weak, answer())])
    assert calibration["balanced_abstention_accuracy"] == 1
    summary = summarize(
        [
            {"metrics": good, "lineage_key": "f", "abstained": False},
            {"metrics": noanswer, "lineage_key": "g", "abstained": True},
        ]
    )
    assert summary["correctness"]["ci95"] == [1, 1]
    assert summary["faithfulness"]["n"] == 1
    assert summary["answered"] == 1


def test_peak_offpeak_cost_is_estimate_not_fabricated_billing() -> None:
    cost = token_cost(
        {"prompt_tokens": 1000, "prompt_cache_hit_tokens": 500, "completion_tokens": 100}
    )
    assert cost["estimated_usd_upper"] == pytest.approx(0.000273)
    assert cost["estimated_usd_lower"] == cost["estimated_usd_upper"] / 2
    assert cost["billed_usd"] is None


def test_correctness_does_not_match_numeric_or_identifier_substrings() -> None:
    wrong = replace(answer(), answer="The max_workers default is 800.")
    assert answer_metrics(wrong, request(), row())["correctness"] == 0
    reference = {**row(), "expected_answer": "max_workers"}
    wrong = replace(answer(), answer="max_workers_other")
    assert answer_metrics(wrong, request(), reference)["correctness"] == 0


def test_faithfulness_scores_delivered_claims_not_stripped_diagnostics() -> None:
    good = answer()
    bad = Claim("max_workers defaults to 800", good.citations)
    mixed = replace(good, answer=good.answer + " " + bad.text, claims=(*good.claims, bad))
    before = answer_metrics(mixed, request(), row())
    assert before["faithfulness"] == 0.5
    verified = verify_answer(mixed, request())
    assert not verified.claims[1].included
    assert answer_metrics(verified, request(), row())["faithfulness"] == 1
    assert verify_answer(verified, request()).answer == verified.answer
