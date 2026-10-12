#!/usr/bin/env python3
"""Build the Phase 4 closeout findings from the current result artifacts."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HEADLINE_SYSTEMS = (
    "default", "bm25", "hybrid-bm25-weighted-025", "scope-explicit", "parent-off",
    "recommended",
)
PARAPHRASE_SYSTEMS = ("bm25", "dense-bge-small", "hybrid-bm25-weighted-025")
METRICS = ("recall@1", "recall@5", "mrr", "ndcg@10", "version_confusion@1")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read JSON artifact {path}: {exc}") from exc


def result_artifact(path: Path) -> dict[str, Any] | None:
    value = read_json(path)
    if not isinstance(value, dict):
        return None
    config = value.get("config")
    if not isinstance(config, dict) or not isinstance(config.get("system"), str):
        return None
    if not isinstance(value.get("rows"), list) or not isinstance(value.get("metrics"), dict):
        return None
    return value


def load_artifacts(results: Path, names: set[str]) -> dict[str, dict[str, Any]]:
    selection = read_json(results / "phase4_selection.json")
    hashes = selection.get("artifact_hashes") if isinstance(selection, dict) else None
    artifacts: dict[str, dict[str, Any]] = {}
    for name in sorted(names):
        candidate: dict[str, Any] | None = None
        if isinstance(hashes, dict) and isinstance(hashes.get(name), str):
            candidate = result_artifact(results / f"{hashes[name]}.json")
        if candidate is None:
            for path in sorted(results.glob("*.json")):
                value = result_artifact(path)
                if value is not None and value["config"]["system"] == name:
                    candidate = value
                    break
        if candidate is None or candidate["config"]["system"] != name:
            raise RuntimeError(f"missing current result artifact for arm {name!r}")
        artifacts[name] = candidate
    return artifacts


def stat_cell(stat: dict[str, Any] | None) -> str:
    if not stat or stat.get("mean") is None or stat.get("ci95") is None:
        return "—"
    low, high = stat["ci95"]
    return f"{stat['mean']:.3f} [{low:.3f}, {high:.3f}]"


def metric(artifact: dict[str, Any], split: str, name: str) -> dict[str, Any]:
    return artifact["metrics"][split]["overall"]["metrics"].get(name, {})


def comparison(
    comparisons: list[dict[str, Any]], left: str, right: str, split: str,
    name: str = "ndcg@10",
) -> dict[str, Any] | None:
    return next((row for row in comparisons if row.get("left") == left
                 and row.get("right") == right and row.get("split") == split
                 and row.get("metric") == name), None)


def difference_cell(row: dict[str, Any] | None) -> str:
    if row is None:
        return "unavailable"
    low, high = row["ci95"]
    interpretation = "CI excludes zero" if not row["within_noise"] else "within noise"
    return f"{row['mean']:+.3f} [{low:+.3f}, {high:+.3f}], {interpretation}"


def headline(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    lines = [
        "## Test headline",
        "",
        "Values are means [lineage-bootstrap 95% CI].",
        "",
        "| System | R@1 | R@5 | MRR | nDCG@10 | Confusion@1 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name in HEADLINE_SYSTEMS:
        lines.append("| " + " | ".join(
            [name] + [stat_cell(metric(artifacts[name], "test", value)) for value in METRICS]
        ) + " |")
    return lines


def findings(artifacts: dict[str, dict[str, Any]], comparisons: list[dict[str, Any]]) -> list[str]:
    lines = ["## Findings", ""]
    pairs = (
        ("recommended", "default", "Recommended versus default"),
        ("recommended", "bm25", "Recommended versus BM25"),
        ("recommended-cross-encoder", "recommended", "Cross-encoder variant versus recommended"),
        ("hybrid-bm25-weighted-025", "default", "Dense plus BM25 hybrid versus default"),
        ("scope-explicit", "default", "Explicit version scope versus default"),
        ("parent-off", "default", "Parent expansion ablation versus default"),
    )
    for left, right, title in pairs:
        lines.append(f"### {title}")
        parts = []
        for split in ("dev", "test"):
            diff = comparison(comparisons, left, right, split)
            parts.append(f"{split}: paired nDCG@10 Δ ({left} − {right}) is "
                         f"{difference_cell(diff)}")
        if left == "recommended-cross-encoder":
            for split in ("dev", "test"):
                base = artifacts[right]["metrics"][split]["overall"]["latency_ms"]["total"]
                variant = artifacts[left]["metrics"][split]["overall"]["latency_ms"]["total"]
                delta = variant["mean"] - base["mean"]
                parts.append(f"{split} total-latency Δ is {delta:+.1f} ms")
        lines.append(" ".join(parts) + ".")
        lines.append("")
    return lines


def paraphrase_table(artifacts: dict[str, dict[str, Any]]) -> list[str]:
    lines = [
        "## Paraphrase breakdown",
        "",
        "`paraphrased=true` is the cohort used to show performance when the parameter "
        "name is absent.",
        "",
        "| System | Split | Paraphrased | Scored n | R@1 | R@5 | MRR | nDCG@10 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name in PARAPHRASE_SYSTEMS:
        for split in ("dev", "test"):
            for flag in ("false", "true"):
                cohort = artifacts[name]["metrics"][split]["paraphrased"][flag]
                lines.append("| " + " | ".join([
                    name, split, flag, str(cohort["metrics"]["mrr"]["n"]),
                    *(stat_cell(cohort["metrics"].get(value))
                      for value in ("recall@1", "recall@5", "mrr", "ndcg@10")),
                ]) + " |")
    return lines


def recommended_types(artifact: dict[str, Any]) -> list[str]:
    lines = [
        "## Recommended by question type (test)",
        "",
        "| Type | Scored n | R@1 | R@5 | MRR | nDCG@10 | Confusion@1 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, cohort in sorted(artifact["metrics"]["test"]["type"].items()):
        lines.append("| " + " | ".join([
            name, str(cohort["metrics"]["mrr"]["n"]),
            *(stat_cell(cohort["metrics"].get(value)) for value in METRICS),
        ]) + " |")
    return lines


def failure_reports(results: Path, selection: dict[str, Any]) -> list[str]:
    names = set(selection.get("best_two", [])) | {"recommended", "recommended-cross-encoder"}
    counts: Counter[str] = Counter()
    examples: defaultdict[str, list[str]] = defaultdict(list)
    reports = []
    for path in sorted(results.glob("failures_*.md")):
        system = path.stem.removeprefix("failures_")
        if system not in names:
            continue
        reports.append(system)
        current_id = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                current_id = line[3:].strip()
            match = re.match(r"\*\*Category:\*\* ([^.]+)\.", line)
            if match:
                category = match.group(1)
                counts[category] += 1
                if len(examples[category]) < 3:
                    examples[category].append(f"{system}/{current_id}")
    report_names = ", ".join(sorted(reports)) or "none"
    lines = ["## Failure categories", "", f"Reports used: {report_names}.", "",
             "Counts are listed failure examples in the current failure reports.", "",
             "| Category | Count | Three examples |", "| --- | ---: | --- |"]
    for category in sorted(counts):
        lines.append(f"| {category} | {counts[category]} | "
                     + ", ".join(f"`{example}`" for example in examples[category]) + " |")
    if not counts:
        lines.append("| none listed | 0 | — |")
    return lines


def limits(preflight: dict[str, Any]) -> list[str]:
    parsed = preflight.get("parsed_version_questions")
    total = preflight.get("gold_rows")
    return [
        "## Limits",
        "",
        "- Questions are model-written from passages and therefore favor lexical overlap.",
        "- Explicit-scope version confusion is zero by construction.",
        f"- Only {parsed} of {total} questions name a version.",
        "- Cohorts are small, so several confidence intervals are wide.",
        "- Some arm rankings flip between DEV and TEST; only differences whose CI "
        "excludes zero count.",
        "- The sparse diagnostic's `gold_ranks` contradicted its own top-3 and is not relied on.",
        "- PostgreSQL full-text ranking is much weaker than BM25.",
    ]


def build(results: Path, output: Path) -> None:
    selection = read_json(results / "phase4_selection.json")
    if not isinstance(selection, dict):
        raise RuntimeError("phase4_selection.json must be an object")
    needed = set(HEADLINE_SYSTEMS) | set(PARAPHRASE_SYSTEMS) | {
        "recommended-cross-encoder"
    }
    artifacts = load_artifacts(results, needed)
    comparison_rows = read_json(results / "phase4_comparisons.json")
    if not isinstance(comparison_rows, list):
        raise RuntimeError("phase4_comparisons.json must be a list")
    preflight = read_json(results / "phase4_preflight.json")
    if not isinstance(preflight, dict):
        raise RuntimeError("phase4_preflight.json must be an object")
    lines = [
        "# Phase 4 findings",
        "",
        "Generated from the current `results/*.json` artifacts; no metrics are hand-copied.",
        "",
    ]
    lines += headline(artifacts) + [""]
    lines += findings(artifacts, comparison_rows)
    lines += paraphrase_table(artifacts) + [""]
    lines += recommended_types(artifacts["recommended"]) + [""]
    lines += failure_reports(results, selection) + [""]
    lines += limits(preflight) + [""]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path, default=Path("docs/phase4_findings.md"))
    args = parser.parse_args()
    build(args.results_dir, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
