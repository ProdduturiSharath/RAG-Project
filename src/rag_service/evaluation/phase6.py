"""Evaluation-only caching, frozen sampling, calibration and transparent proxy metrics."""

from __future__ import annotations

import hashlib
import json
import re
import statistics
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rag_service.generation.models import GeneratedAnswer, GenerationRequest
from rag_service.generation.openai_compatible import MODEL, OpenAICompatibleGenerator, parse_answer
from rag_service.generation.verification import (
    annotate,
    evidence_confidence,
    lexical_support,
    quote_valid,
    verify_answer,
    words,
)

from .metrics import bootstrap
from .phase4_data import atomic_json, digest

METRICS = (
    "correctness",
    "faithfulness",
    "citation_precision",
    "abstention_correctness",
    "wrong_version_answers",
)
PRICE_SOURCE = "https://api-docs.deepseek.com/quick_start/pricing"


def token_cost(usage: dict[str, Any]) -> dict[str, Any]:
    """Verified public token rates; range covers peak/off-peak, not account billing."""
    prompt = int(usage.get("prompt_tokens", 0))
    hits = int(usage.get("prompt_cache_hit_tokens", 0))
    misses = int(usage.get("prompt_cache_miss_tokens", prompt - hits))
    output = int(usage.get("completion_tokens", 0))
    peak = (hits * 0.006 + misses * 0.30 + output * 1.20) / 1_000_000
    return {
        "estimated_usd_upper": peak,
        "estimated_usd_lower": peak / 2,
        "billed_usd": None,
        "source": PRICE_SOURCE,
        "basis": "public peak/off-peak rates; granted balance/billing not observable",
    }


class EvaluationCache:
    """Never constructed or imported by the serving stack. Errors are never persisted."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def identity(
        self, generator: OpenAICompatibleGenerator, request: GenerationRequest, question_id: str
    ) -> dict[str, Any]:
        payload = generator.payload(request)
        # Include full generation controls and the fixed prompt, not just question text.
        return {
            "model": MODEL,
            "prompt_hash": digest(payload),
            "question_id": question_id,
            "context_hash": digest([asdict(m.chunk) for m in request.matches]),
        }

    async def generate(
        self, generator: OpenAICompatibleGenerator, request: GenerationRequest, question_id: str
    ) -> tuple[GeneratedAnswer, bool]:
        if generator.verified:
            raise ValueError("cache raw completions only; verification must use current code")
        identity = self.identity(generator, request, question_id)
        path = self.root / "generation" / f"{digest(identity)}.json"
        if path.exists():
            entry = json.loads(path.read_text(encoding="utf-8"))
            if entry["identity"] != identity or entry.get("format") != 1:
                raise ValueError("cache identity/format mismatch")
            answer = parse_answer(json.dumps(entry["response"]), entry["metadata"])
            return answer, True
        answer = await generator.generate(request)
        if "usage" not in answer.metadata:
            return answer, False  # Local policy abstention is not an LLM call.
        metadata = {**answer.metadata, "cost": token_cost(answer.metadata["usage"])}
        response = {
            "answer": answer.answer,
            "answered_version": answer.answered_version,
            "claims": [
                {
                    "text": c.text,
                    "citations": [
                        {
                            "chunk_id": cite.chunk_id,
                            "document_id": cite.document_id,
                            "version": cite.version,
                            "section_path": list(cite.section_path),
                            "quote": cite.excerpt,
                        }
                        for cite in c.citations
                    ],
                }
                for c in answer.claims
            ],
        }
        # Parse before committing, including schema errors and incomplete streams.
        parsed = parse_answer(json.dumps(response), metadata)
        atomic_json(
            path, {"format": 1, "identity": identity, "response": response, "metadata": metadata}
        )
        return parsed, False


def freeze_subset(rows: list[dict[str, Any]], path: Path) -> dict[str, Any]:
    """Outcome-independent quotas, including all 12 negative test rows and 2 human rows."""
    test = [r for r in rows if r["split"] == "test"]
    quotas = {
        "unanswerable": 4,
        "version_unavailable": 8,
        "acl": 4,
        "multi_hop": 2,
        "table": 5,
        "exact_identifier": 10,
        "factoid": 10,
        "unchanged_control": 6,
        "version_specific": 11,
    }
    selected = []
    for kind, count in quotas.items():
        group = sorted(
            (r for r in test if r["type"] == kind),
            key=lambda r: (
                r["review_method"] != "human",
                hashlib.sha256(("phase6-v1:" + r["id"]).encode()).hexdigest(),
            ),
        )
        if len(group) < count:
            raise ValueError(f"insufficient test rows: {kind}")
        selected.extend(group[:count])
    selected.sort(key=lambda r: r["id"])
    manifest = {
        "format": 1,
        "seed": "phase6-v1",
        "quotas": quotas,
        "gold_hash": digest(rows),
        "ids": [r["id"] for r in selected],
        "rule": "type quotas; human-reviewed first, then SHA256(seed:id); no outcomes",
    }
    if len(selected) != 60 or sum(not r["answerability"] for r in selected) != 12:
        raise ValueError("subset must contain 60 test rows including all 12 negatives")
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError("frozen subset drift; review manifest explicitly")
    if not path.exists():
        atomic_json(path, manifest)
    return manifest


def expected_abstention(row: dict[str, Any]) -> bool:
    return not row["answerability"] or not row["acl_allowance"]


def answer_metrics(
    answer: GeneratedAnswer, request: GenerationRequest, row: dict[str, Any]
) -> dict[str, float | None]:
    """Lexical reference matching and quote support proxies, never an LLM judge."""
    marked = annotate(answer, request)
    denied = expected_abstention(row)
    abstained = marked.abstained
    citations = marked.citations
    included = [claim for claim in marked.claims if claim.included]
    wrong_version = not abstained and (
        marked.answered_version != row["target_version"]
        or any(c.version != row["target_version"] for c in citations)
    )
    # Baseline has no version field: its retrieved citations supply the answered version.
    if not abstained and answer.answered_version is None and citations:
        wrong_version = any(c.version != row["target_version"] for c in citations)
    expected = str(row["expected_answer"])
    normalized = " ".join(marked.answer.casefold().split())
    reference = " ".join(expected.casefold().split())
    # Prevent numbers/identifiers and polarity mismatches passing a loose token score.
    overlap = lexical_support(expected, marked.answer)
    correct = (
        abstained
        if denied
        else (
            not abstained
            and not wrong_version
            and (
                re.search(r"(?<!\w)" + re.escape(reference) + r"(?!\w)", normalized) is not None
                or (overlap >= 0.8 and len(words(expected)) >= 3)
            )
        )
    )
    return {
        "correctness": float(correct),
        "faithfulness": None
        if abstained
        else (sum(c.supported for c in included) / max(1, len(included))),
        "citation_precision": None
        if abstained
        else (
            sum(quote_valid(c, request) and c.version == row["target_version"] for c in citations)
            / max(1, len(citations))
        ),
        "abstention_correctness": float(abstained == denied),
        "wrong_version_answers": float(wrong_version),
    }


def calibrate(
    items: list[tuple[dict[str, Any], GenerationRequest, GeneratedAnswer]],
) -> dict[str, Any]:
    if not items or any(row["split"] != "dev" for row, _, _ in items):
        raise ValueError("calibration accepts dev only")
    grid = []
    for threshold in [i / 20 for i in range(21)]:
        positives: list[float] = []
        negatives: list[float] = []
        for row, request, answer in items:
            result = verify_answer(answer, request, threshold=threshold)
            correct = result.abstained == expected_abstention(row)
            (negatives if expected_abstention(row) else positives).append(float(correct))
        score = (statistics.fmean(positives) + statistics.fmean(negatives)) / 2
        grid.append({"threshold": threshold, "balanced_abstention_accuracy": score})
    best = max(grid, key=lambda r: (r["balanced_abstention_accuracy"], -r["threshold"]))
    return {
        **best,
        "split": "dev",
        "rows": len(items),
        "grid": grid,
        "objective": "balanced answerable/should-abstain decision accuracy; lowest tie threshold",
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {"n": len(rows), "answered": sum(not r["abstained"] for r in rows)}
    for metric in METRICS:
        scored = [r for r in rows if r["metrics"][metric] is not None]
        result[metric] = bootstrap(
            [float(r["metrics"][metric]) for r in scored],
            [r["lineage_key"] for r in scored],
            seed=42,
            samples=2000,
        )
    return result


def scored_record(
    row: dict[str, Any],
    request: GenerationRequest,
    answer: GeneratedAnswer,
    arm: str,
    wall_seconds: float,
) -> dict[str, Any]:
    return {
        "id": row["id"],
        "split": row["split"],
        "type": row["type"],
        "lineage_key": row["lineage_key"],
        "review_method": row["review_method"],
        "arm": arm,
        **asdict(answer),
        "metrics": answer_metrics(answer, request, row),
        "wall_seconds": wall_seconds,
        "evidence_confidence": evidence_confidence(request),
    }


def fingerprint_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def elapsed(started: float) -> float:
    return time.perf_counter() - started


def subset_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(row["type"] for row in rows).items()))
