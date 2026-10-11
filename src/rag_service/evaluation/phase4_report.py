"""Cohort summaries, paired comparisons, and reproducible failure reports."""

from __future__ import annotations

import itertools
import re
from pathlib import Path
from typing import Any

import numpy as np

from .metrics import KS, bootstrap, normalize, paired_bootstrap
from .phase4_config import MODEL_CARD_URL
from .phase4_data import atomic_json

RETRIEVAL_METRICS = [*(f"recall@{k}" for k in KS), "mrr", "ndcg@10"]
EXTRA_METRICS = [*(f"all_quotes@{k}" for k in KS),
                 *(f"version_confusion@{k}" for k in KS),
                 "correct_version_recall@1", "top1_different_lineage@1",
                 "false_exclusion"]


def distribution(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"n": 0, "mean": None, "quantiles": None, "values": []}
    return {"n": len(values), "mean": float(np.mean(values)), "values": values,
            "quantiles": dict(zip(("min", "p05", "p25", "p50", "p75", "p95", "max"),
                                  np.quantile(values, [0, .05, .25, .5, .75, .95, 1]).tolist(),
                                  strict=True))}


def cohort(rows: list[dict[str, Any]], seed: int, samples: int) -> dict[str, Any]:
    output: dict[str, Any] = {"n": len(rows), "metrics": {},
                              "acl_leakage_count": sum(row["leakage_count"] for row in rows)}
    for metric in RETRIEVAL_METRICS + EXTRA_METRICS:
        eligible = [row for row in rows if metric in row["metrics"]]
        output["metrics"][metric] = bootstrap(
            [row["metrics"][metric] for row in eligible], [row["lineage_key"] for row in eligible],
            seed=seed, samples=samples,
        )
    output["top1_scores"] = {}
    for kind in ("unanswerable", "version_unavailable"):
        subset = [row for row in rows if row["type"] == kind]
        output["top1_scores"][kind] = {
            "questions": len(subset), "no_result": sum(row["top1_score"] is None for row in subset),
            **{key: distribution([row[key] for row in subset if row[key] is not None])
               for key in ("top1_score", "top1_dense_score", "top1_sparse_score")},
        }
    hops = [row for row in rows if row["type"] == "multi_hop"]
    denominator = sum(len(row["evidence_spans"]) for row in hops)
    output["multi_hop_quote_share"] = {
        str(k): (sum(row["metrics"][f"recall@{k}"] * len(row["evidence_spans"])
                     for row in hops) / denominator if denominator else None) for k in KS
    }
    output["latency_ms"] = {}
    for stage in sorted({stage for row in rows for stage in row["latency_ms"]}):
        timed = [row for row in rows if stage in row["latency_ms"]]
        values = [row["latency_ms"][stage] for row in timed]
        output["latency_ms"][stage] = {
            **bootstrap(values, [row["lineage_key"] for row in timed], seed=seed, samples=samples),
            "p50": float(np.quantile(values, .5)), "p95": float(np.quantile(values, .95)),
        }
    return output


def summarize(rows: list[dict[str, Any]], seed: int, samples: int) -> dict[str, Any]:
    output = {}
    for split in ("dev", "test"):
        subset = [row for row in rows if row["split"] == split]
        kinds = sorted({row["type"] for row in rows})
        output[split] = {
            "overall": cohort(subset, seed, samples),
            "type": {kind: cohort([r for r in subset if r["type"] == kind], seed, samples)
                     for kind in kinds},
            "paraphrased": {
                str(flag).lower(): cohort([r for r in subset if r["paraphrased"] == flag],
                                          seed, samples)
                for flag in (False, True)
            },
            "type_paraphrased": {
                f"{kind}/{str(flag).lower()}": cohort(
                    [r for r in subset if r["type"] == kind and r["paraphrased"] == flag],
                    seed, samples)
                for kind, flag in itertools.product(kinds, (False, True))
            },
            "review_method": {method: cohort([r for r in subset if r["review_method"] == method],
                                               seed, samples)
                              for method in ("human", "model_audit", "owner_written")},
            "human_or_owner_written": cohort(
                [r for r in subset if r["review_method"] in {"human", "owner_written"}],
                seed, samples),
        }
    return output


def comparisons(artifacts: dict[str, dict[str, Any]], parents: dict[str, str], best: list[str],
                seed: int, samples: int) -> list[dict[str, Any]]:
    pairs = {(name, "default") for name in artifacts if name != "default"}
    pairs |= {(name, parent) for name, parent in parents.items() if name in artifacts}
    pairs |= {(name, "bm25") for name in ("recommended", "recommended-cross-encoder")
              if name in artifacts and "bm25" in artifacts}
    if len(best) == 2:
        pairs.add((best[0], best[1]))
    output = []
    for left, right in sorted(pairs):
        for split in ("dev", "test"):
            a = [r for r in artifacts[left]["rows"] if r["split"] == split]
            b = [r for r in artifacts[right]["rows"] if r["split"] == split]
            if not a or not b:
                continue
            for metric in RETRIEVAL_METRICS + [f"version_confusion@{k}" for k in KS]:
                difference = paired_bootstrap(a, b, metric, seed=seed, samples=samples)
                output.append({"left": left, "right": right, "split": split,
                               "metric": metric, **difference})
    return output


def failure_category(row: dict[str, Any]) -> tuple[str, str]:
    if row["metrics"].get("version_confusion@10", 0):
        return "wrong version", "A same-lineage wrong version outranks the first correct evidence."
    if row["relevant_chunk_count"] == 0:
        return "text gap", "No authorized, version-valid chunk contains a whole evidence quote."
    if row["type"] == "exact_identifier":
        text = " ".join(r["text"] for r in row["retrieved"][:3]).casefold()
        identifiers = re.findall(r"[A-Za-z][A-Za-z0-9]*_[A-Za-z0-9_]+", row["expected_answer"])
        if identifiers and not any(identifier.casefold() in text for identifier in identifiers):
            return "identifier not matched", "The expected identifier is absent from the top three."
    return "other", "Evidence exists but ranking/scoping does not place it early enough."


def write_failures(name: str, rows: list[dict[str, Any]], results: Path) -> None:
    failures = [row for row in rows if row["split"] == "test" and "ndcg@10" in row["metrics"]
                and (row["metrics"]["all_quotes@10"] < 1 or row["metrics"]["mrr"] < 1
                     or row["metrics"]["ndcg@10"] < 1)]
    failures.sort(key=lambda row: (row["metrics"]["all_quotes@10"], row["metrics"]["recall@10"],
                                  row["metrics"]["ndcg@10"], row["metrics"]["mrr"], row["id"]))
    lines = [f"# Worst test failures: {name}", "",
             f"DEV-selected system or fixed DEV-derived combined arm. "
             f"Showing {min(30, len(failures))} "
             f"of {len(failures)} failures.",
             "Ranking: all-quotes@10, Recall@10, nDCG@10, MRR ascending; then ID.", ""]
    for row in failures[:30]:
        category, reason = failure_category(row)
        lines += [f"## {row['id']}", "", row["question"], "",
                  f"**Category:** {category}. **Reason:** {reason}", "",
                  f"Target: {row['target_version']}; gold versions: {row.get('gold_versions', [])}",
                  "", "### Expected evidence"]
        lines += [f"- ({span.get('version', row['target_version'])}) {normalize(span['quote'])}"
                  for span in row["evidence_spans"]]
        lines += ["", "### Top three retrieved"]
        for rank, chunk in enumerate(row["retrieved"][:3], 1):
            lines += [f"{rank}. `{chunk['chunk_id']}` — {chunk['version']}; "
                      f"score={chunk['score']:.6f}, dense={chunk['dense_score']:.6f}, "
                      f"sparse={chunk['sparse_score']:.6f}, rerank={chunk['rerank_score']}", "",
                      "> " + normalize(chunk["text"]), ""]
        if not row["retrieved"]:
            lines += ["No results returned.", ""]
    (results / f"failures_{name}.md").write_text("\n".join(lines) + "\n")


def cell(result: dict[str, Any]) -> str:
    if result["mean"] is None:
        return "—"
    low, high = result["ci95"]
    return f"{result['mean']:.3f} [{low:.3f}, {high:.3f}]"


def write_table(artifacts: dict[str, dict[str, Any]], parents: dict[str, str], best: list[str],
                alpha: str, differences: list[dict[str, Any]], results: Path,
                skipped: list[str], scifact: dict[str, Any] | None = None) -> Path:
    provenance = next(iter(artifacts.values())).get("provenance", {})
    parsed_count = provenance.get("parsed_version_questions")
    total_gold = provenance.get("gold_rows")
    lines = ["# Phase 4 retrieval evaluation", "",
             "Values are means [lineage-bootstrap 95% CI]; intervals containing zero for paired "
             "differences are marked within noise. Scores use a 0–1 scale.", "",
             f"**DEV-selected alpha arms:** {alpha}. **DEV-selected best two:** {', '.join(best)}.",
             f"**Gold questions with a parsed version:** {parsed_count} / {total_gold}.",
             "", "MRR is over the returned list (default 30); Recall is evidence-quote coverage. "
             "Models are warmed; cached latency retains the original run's measurements.", "",
             f"BGE guidance: [{MODEL_CARD_URL}]({MODEL_CARD_URL}); instruction was already on.", "",
             "Skipped flagged arms: " + (", ".join(skipped) or "none") + ".", ""]
    header = ("| System | Parent | Split | Scored n | R@1 | R@3 | R@5 | R@10 | MRR | "
              "Correct-version R@1 | Confusion@1 | Top-1 other lineage | nDCG@10 | Leakage |")
    lines += [header, "|" + " --- |" * 15]
    for name, artifact in artifacts.items():
        for split in ("dev", "test"):
            summary = artifact["metrics"][split]["overall"]
            if not summary["n"]:
                continue
            metrics = summary["metrics"]
            cells = [name, parents.get(name, "—"), split, str(metrics["mrr"]["n"]),
                     *(cell(metrics[m]) for m in ("recall@1", "recall@3", "recall@5",
                                                  "recall@10", "mrr")),
                     cell(metrics["correct_version_recall@1"]),
                     cell(metrics["version_confusion@1"]),
                     cell(metrics["top1_different_lineage@1"]),
                     cell(metrics["ndcg@10"]), str(summary["acl_leakage_count"])]
            lines.append("| " + " | ".join(cells) + " |")
    lines += ["", "## Paired nDCG@10 differences", "",
              "| Left − right | Split | Difference [95% CI] | Interpretation |",
              "| --- | --- | --- | --- |"]
    for row in differences:
        if row["metric"] == "ndcg@10":
            lines.append(f"| {row['left']} − {row['right']} | {row['split']} | {cell(row)} | "
                         f"{'within noise' if row['within_noise'] else 'CI excludes zero'} |")
    for name, artifact in artifacts.items():
        lines += ["", f"## {name}", "", f"Artifact: `{artifact['config_hash']}.json`", "",
                  "| Split/cohort | Questions / scored | R@1 | R@3 | R@5 | R@10 | MRR | nDCG@10 |",
                  "|" + " --- |" * 8]
        for split in ("dev", "test"):
            summaries = artifact["metrics"][split]
            if not summaries["overall"]["n"]:
                continue
            for group in ("type", "paraphrased", "type_paraphrased", "review_method"):
                for key, summary in summaries[group].items():
                    lines.append("| " + " | ".join([
                        f"{split}/{group}/{key}",
                        f"{summary['n']} / {summary['metrics']['mrr']['n']}",
                        *(cell(summary["metrics"][m]) for m in RETRIEVAL_METRICS),
                    ]) + " |")
            human = summaries["human_or_owner_written"]
            lines.append("| " + " | ".join([f"{split}/human+owner",
                         f"{human['n']} / {human['metrics']['mrr']['n']}",
                         *(cell(human["metrics"][m]) for m in RETRIEVAL_METRICS)]) + " |")
        lines += ["", "### Multi-hop, version scope, and latency", ""]
        for split in ("dev", "test"):
            summaries = artifact["metrics"][split]
            overall = summaries["overall"]
            if not overall["n"]:
                continue
            lines += [f"**{split}**", ""]
            for metric in [f"version_confusion@{k}" for k in KS] + ["false_exclusion"]:
                value = overall["metrics"][metric]
                lines.append(f"- {metric}: {cell(value)} (n={value['n']})")
            hops = summaries["type"].get("multi_hop")
            if hops:
                for k in KS:
                    lines.append(f"- Multi-hop @{k}: quote share "
                                 f"{cell(hops['metrics'][f'recall@{k}'])}; "
                                 f"all quotes {cell(hops['metrics'][f'all_quotes@{k}'])}")
            for stage, timing in overall["latency_ms"].items():
                lines.append(f"- {stage} ms: {cell(timing)}; p50={timing['p50']:.2f}, "
                             f"p95={timing['p95']:.2f}")
            for kind, scores in overall["top1_scores"].items():
                final = scores["top1_score"]
                lines.append(f"- {kind} top-1 scores: n={final['n']}, "
                             f"no result={scores['no_result']}, "
                             f"mean={final['mean']}, quantiles={final['quantiles']}")
            lines.append("")
    if scifact is not None:
        lines += ["## SciFact sanity check (last)", "",
                  "| Model | Measured nDCG@10 | Published nDCG@10 |",
                  "| --- | --- | --- |",
                  f"| BGE-small-en-v1.5 | {scifact['ndcg@10']:.5f} | "
                  f"{scifact['published_ndcg@10']:.5f} |", "",
                  f"Dataset: {scifact['dataset_url']}",
                  f"Published: {scifact['model_card_url']}", ""]
    path = results / "phase4_table.md"
    temporary = path.with_suffix(".md.tmp")
    temporary.write_text("\n".join(lines) + "\n")
    temporary.replace(path)
    atomic_json(results / "phase4_comparisons.json", differences)
    return path
