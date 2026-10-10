"""Pure evidence metrics and lineage-clustered, paired bootstrap intervals."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

KS = (1, 3, 5, 10)
SCORED_TYPES = {
    "factoid", "exact_identifier", "table", "multi_hop", "version_specific", "unchanged_control",
}


def normalize(text: str) -> str:
    return " ".join(text.split())


def covers(row: Mapping[str, Any], chunk: Mapping[str, Any]) -> frozenset[int]:
    """Text containment, case preserved, plus the question's version rule.

    Lineage is deliberately not an extra hit requirement: an equivalent quote
    elsewhere in the corpus is evidence too. Lineage *is* required for confusion.
    """
    independent = row["version_independent"] and row.get("type") != "version_specific"
    versions = row["gold_versions"] if independent else [row["target_version"]]
    if chunk["version"] not in versions:
        return frozenset()
    text = chunk.get("normalized_text")
    if text is None:
        text = normalize(chunk["text"])
    return frozenset(i for i, span in enumerate(row["evidence_spans"])
                     if normalize(span["quote"]) and normalize(span["quote"]) in text)


def version_confusion(row: Mapping[str, Any], ranked: Sequence[Mapping[str, Any]], k: int) -> int:
    """Any same-lineage wrong version above the first Correct (missing = infinity)."""
    first_correct = next((i for i, chunk in enumerate(ranked) if covers(row, chunk)), len(ranked))
    lineages = {row["lineage_key"]} | {
        span.get("lineage_key", row["lineage_key"]) for span in row["evidence_spans"]
    }
    return int(any(chunk.get("lineage_key") in lineages
                   and chunk["version"] != row["target_version"]
                   for chunk in ranked[:min(k, first_correct)]))


def ndcg(relevance: Sequence[float], ideal: Sequence[float], k: int = 10) -> float:
    """Linear-gain nDCG (binary for gold, BEIR relevance grades for SciFact)."""
    def dcg(values: Sequence[float]) -> float:
        return sum(float(value) / math.log2(rank + 2) for rank, value in enumerate(values[:k]))

    denominator = dcg(sorted(ideal, reverse=True))
    return dcg(relevance) / denominator if denominator else 0.0


def score_question(row: Mapping[str, Any], ranked: Sequence[Mapping[str, Any]],
                   relevant_count: int) -> dict[str, float]:
    if row["type"] not in SCORED_TYPES and not (row["type"] == "acl" and row["acl_allowance"]):
        return {}
    total = len(row["evidence_spans"])
    if not total:
        raise ValueError(f"scored question has no evidence: {row['id']}")
    coverage = [covers(row, chunk) for chunk in ranked]
    scores: dict[str, float] = {}
    for k in KS:
        found = set().union(*coverage[:k])
        scores[f"recall@{k}"] = len(found) / total
        scores[f"all_quotes@{k}"] = float(len(found) == total)
    scores["mrr"] = next((1 / rank for rank, found in enumerate(coverage, 1) if found), 0.0)
    scores["ndcg@10"] = ndcg([float(bool(found)) for found in coverage],
                             [1.0] * min(relevant_count, 10))
    if row["type"] == "version_specific":
        scores.update({f"version_confusion@{k}": float(version_confusion(row, ranked, k))
                       for k in KS})
    return scores


def bootstrap(values: Sequence[float], lineages: Sequence[str], *, seed: int = 42,
              samples: int = 2000) -> dict[str, Any]:
    """Resample whole lineages, retaining every row and its multiplicity.

    The estimand is the question-weighted mean, not the mean of lineage means.
    Sorting clusters makes intervals invariant to input order.
    """
    if len(values) != len(lineages) or samples < 1:
        raise ValueError("aligned values/lineages and positive bootstrap samples required")
    if not values:
        return {"mean": None, "ci95": None, "n": 0, "lineages": 0}
    groups: dict[str, list[float]] = {}
    for key, value in zip(lineages, values, strict=True):
        if not math.isfinite(value):
            raise ValueError("bootstrap values must be finite")
        groups.setdefault(key, []).append(float(value))
    ordered = [groups[key] for key in sorted(groups)]
    sums = np.array([math.fsum(group) for group in ordered])
    counts = np.array([len(group) for group in ordered])
    draws = np.random.default_rng(seed).integers(0, len(ordered), (samples, len(ordered)))
    estimates = sums[draws].sum(axis=1) / counts[draws].sum(axis=1)
    return {"mean": math.fsum(values) / len(values),
            "ci95": np.quantile(estimates, [0.025, 0.975]).tolist(),
            "n": len(values), "lineages": len(groups)}


def paired_bootstrap(left: Sequence[Mapping[str, Any]], right: Sequence[Mapping[str, Any]],
                     metric: str, *, seed: int = 42, samples: int = 2000) -> dict[str, Any]:
    """Left minus right, with the same sampled lineages in both systems."""
    a = {row["id"]: row for row in left if metric in row["metrics"]}
    b = {row["id"]: row for row in right if metric in row["metrics"]}
    if a.keys() != b.keys():
        raise ValueError("paired comparison requires identical question IDs")
    keys = sorted(a)
    if any(a[key]["lineage_key"] != b[key]["lineage_key"] for key in keys):
        raise ValueError("paired question lineages differ")
    result = bootstrap([a[key]["metrics"][metric] - b[key]["metrics"][metric] for key in keys],
                       [a[key]["lineage_key"] for key in keys], seed=seed, samples=samples)
    interval = result["ci95"]
    result["within_noise"] = None if interval is None else interval[0] <= 0 <= interval[1]
    return result
