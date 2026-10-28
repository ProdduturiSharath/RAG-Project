#!/usr/bin/env python3
"""Phase 6: frozen local retrieval, streamed DeepSeek answers and dev-only calibration."""

from __future__ import annotations

import asyncio
import json
import os
import statistics
import time
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

from rag_service.domain import AccessPolicy
from rag_service.evaluation.phase4_data import allowed, atomic_json, digest
from rag_service.evaluation.phase6 import (
    METRICS,
    EvaluationCache,
    calibrate,
    fingerprint_file,
    freeze_subset,
    scored_record,
    subset_counts,
    summarize,
)
from rag_service.generation.extractive import ExtractiveAnswerGenerator
from rag_service.generation.models import GeneratedAnswer, GenerationRequest
from rag_service.generation.openai_compatible import ENDPOINT, MODEL, OpenAICompatibleGenerator
from rag_service.generation.verification import abstention, annotate, verify_answer
from rag_service.retrieval.models import RetrievalFilters, ScoredChunk
from scripts.phase5_eval import (
    DATABASE_DEFAULT,
    build_dense_matrix,
    chunk_records,
    load_acl_policy,
    load_base_vectors,
    load_chunks,
    load_vectors,
    policy_groups,
    rank_hybrid,
)

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("extractive", "extractive-verified", "llm-unverified", "llm-verified")


class RetrievalSnapshot:
    """Read-only corpus, existing BGE vectors and one BM25 index per authorized scope."""

    def __init__(self) -> None:
        dsn = os.environ.get("RAG_EVAL_DATABASE_URL", DATABASE_DEFAULT)
        with psycopg.connect(dsn, connect_timeout=5, row_factory=dict_row) as connection:
            connection.execute("SET TRANSACTION READ ONLY")
            private = connection.execute("""SELECT count(*) AS n FROM public.document_versions v
                WHERE v.status='active' AND NOT EXISTS (SELECT 1 FROM public.acl a
                WHERE a.document_version_id=v.id AND a.is_public)""").fetchone()
            if private is None or private["n"]:
                raise ValueError("Phase 6 external evaluation requires a wholly public corpus")
            self.chunks = [
                replace(c, access_policy=AccessPolicy(public=True)) for c in load_chunks(connection)
            ]
            self.vectors = load_base_vectors(connection, "bge-small-en-v1.5")
        self.records = chunk_records(self.chunks)
        self.matrix = build_dense_matrix(self.records, self.vectors)
        self.queries, index = load_vectors(
            ROOT / "phase5_outputs", "baseline-bge-small", eval_queries=True
        )
        self.policy = load_acl_policy()
        self.scopes: dict[tuple[str | None, str], tuple[list, list]] = {}
        self.by_id = {chunk.chunk_id: chunk for chunk in self.chunks}
        self.provenance = {
            "chunks": len(self.chunks),
            "embedder": "bge-small-en-v1.5",
            "query_index": index,
            "corpus_hash": digest(self.records),
            "policy_hash": digest(self.policy),
            "alpha": 0.5,
            "top_k": 5,
            "scope": "explicit target_version from benchmark request",
        }

    def retrieve(self, row: dict[str, Any]) -> GenerationRequest:
        requester = row["requester"] if row["type"] == "acl" else None
        groups = policy_groups(self.policy, requester) if requester else ()
        filters = RetrievalFilters(
            principal=requester,
            groups=groups,
            product_version=row["target_version"],
            version_mode="explicit",
        )
        # ACL cases target the simulated restricted collection, not an unrelated public corpus.
        # Derive denial from policy, never from answerability or expected-answer labels.
        if requester and not set(groups) & set(self.policy["restricted_allowed_groups"]):
            return GenerationRequest(
                row["question"], (), filters=filters, answered_version=row["target_version"]
            )
        key = (requester, row["target_version"])
        if key not in self.scopes:
            chunks = [
                c
                for c in self.chunks
                if c.version == row["target_version"]
                and (requester is None or allowed(c, self.policy, requester))
            ]
            ids = {c.chunk_id for c in chunks}
            self.scopes[key] = (chunks, [r for r in self.records if r["chunk_id"] in ids])
        chunks, records = self.scopes[key]
        query = self.queries.get(row["id"])
        if query is None:
            raise ValueError(f"missing frozen Phase 5 query vector for {row['id']}")
        ranked = rank_hybrid(
            row["question"], query, chunks, records, self.vectors, 0.5, dense_matrix=self.matrix
        )
        matches = tuple(
            ScoredChunk(self.by_id[r["chunk_id"]], hybrid_score=r["score"], rank=i)
            for i, r in enumerate(ranked[:5], 1)
        )
        if requester and any(not allowed(m.chunk, self.policy, requester) for m in matches):
            raise ValueError("ACL leakage in retrieved context")
        return GenerationRequest(
            row["question"], matches, filters=filters, answered_version=row["target_version"]
        )


def cell(metric: dict[str, Any]) -> str:
    if metric["mean"] is None:
        return "—"
    low, high = metric["ci95"]
    return f"{metric['mean']:.3f} [{low:.3f}, {high:.3f}]"


def reports(result: dict[str, Any]) -> tuple[str, str]:
    table = [
        "# Phase 6 results",
        "",
        "Frozen 60-question test set; mean [bootstrap 95% CI].",
        "",
        "| Arm | Correctness* | Faithfulness* | Citation precision* | Abstention correctness | "
        "Wrong-version answers | Answered |",
        "| --- | --- | --- | --- | --- | --- | ---: |",
    ]
    for arm in ARMS:
        summary = result["test_summaries"][arm]
        table.append(
            "| "
            + " | ".join([arm, *(cell(summary[m]) for m in METRICS), str(summary["answered"])])
            + " |"
        )
    table += [
        "",
        "*Deterministic lexical-reference / quote-support proxies, not human semantic "
        "judgments. Faithfulness and citation precision exclude abstentions.",
        "Wrong-version rate uses all 60 questions as denominator. CIs resample lineage "
        "clusters (2,000 draws, seed 42).",
        "",
    ]
    dev = result["dev_decision"]
    lines = [
        "# Phase 6 findings",
        "",
        "Generated from `results/phase6_results.json`.",
        "",
        "## Protocol",
        "",
        f"- Provider: `{ENDPOINT}`; model `{MODEL}` only.",
        "- `temperature=0`, `stream=true`, `thinking.type=disabled`; 45s total deadline per "
        "HTTP attempt, at most 3 attempts; 0.5s start throttle, 429/5xx exponential backoff.",
        "- JSON answers include answered_version, atomic claims, exact document/version/section/"
        "chunk identifiers and verbatim quotes. Raw reasoning is neither requested nor stored.",
        "- All 115 dev rows calibrate separate extractive and LLM abstention thresholds. "
        "Threshold selection maximizes balanced answerable/should-abstain decision accuracy; "
        "test outcomes never select a threshold, prompt, subset, or retrieval arm.",
        f"- Thresholds: extractive={result['calibration']['extractive']['threshold']:.2f}; "
        f"LLM={result['calibration']['llm']['threshold']:.2f}.",
        "- The 60 test IDs are frozen in `data/eval/phase6_subset.json` before generation, "
        "stratified by type, retaining every negative and both human-reviewed test rows.",
        f"- Test type counts: `{json.dumps(result['subset_counts'], sort_keys=True)}`.",
        "- Reuses the Phase 5 BGE-small query vectors, existing Postgres BGE-small corpus "
        "vectors, cached BM25 and vectorized scoring; weighted alpha=0.5, top 5, explicit "
        "requested target_version. No training or GPU stage is run. Database reads only.",
        "- Four arms share identical authorized/scoped context. The two LLM arms share one "
        "raw completion per question; verification is entirely local.",
        "- ACL cohorts request the simulated restricted collection. Policy denies 8 "
        "requesters (5 dev, 3 selected test), which abstain without provider access. Actual "
        "private corpora fail preflight. No unauthorized chunks are sent.",
        "",
        "## Test results",
        "",
        *table[4:],
        "Verification trades coverage for lexical support: compare the answered count and "
        "correctness with the unverified arm; a higher conditional support score alone is not "
        "an answer-quality improvement.",
        "",
        "## Dev model / cost decision",
        "",
        f"- Decision: **{dev['selected']}**. Rule: prefer verified LLM only if dev correctness "
        "proxy gains at least 0.02 and wrong-version rate does not increase.",
        f"- Dev verified correctness: extractive={dev['extractive_correctness']:.3f}, "
        f"LLM={dev['llm_correctness']:.3f}.",
        f"- Dev median generation latency: extractive={dev['extractive_median_seconds']:.4f}s, "
        f"LLM={dev['llm_median_seconds']:.3f}s (provider-recorded latency, including retries).",
        f"- Dev LLM token-cost estimate: ${dev['cost_lower_usd']:.6f}–"
        f"${dev['cost_upper_usd']:.6f}; extractive API cost $0.",
        f"- All dev+test successful LLM responses: {result['usage']['calls']}; token-cost "
        f"estimate ${result['usage']['cost_lower_usd']:.6f}–"
        f"${result['usage']['cost_upper_usd']:.6f}. Billed dollars / granted balance are unknown.",
        "- Rates from https://api-docs.deepseek.com/quick_start/pricing: per million tokens "
        "$0.003–0.006 input cache-hit, $0.15–0.30 input cache-miss, $0.60–1.20 output. "
        "Do not interpret the estimate as proof of free-tier usage.",
        "",
        "## Human-reviewed alignment",
        "",
        "The existing four human-reviewed gold rows (2 dev, 2 test) are evaluated separately. "
        "These are reference-answer alignments, not newly collected human ratings of generated "
        "answers and not an LLM-judge agreement study.",
    ]
    for arm in ARMS:
        summary = result["human_alignment"][arm]
        lines.append(
            f"- {arm}: n={summary['n']}, correctness proxy {cell(summary['correctness'])}."
        )
    lines += [
        "",
        "## Verification, cache and serving",
        "",
        "- Exact quotes and document/version/section/chunk identity must match transmitted "
        "authorized evidence. Claim support uses token overlap plus numeric, identifier and "
        "negation guards. Unsupported claims are stripped from answer text and retained as "
        "flagged claim diagnostics (`included=false`); faithfulness scores only delivered claims. "
        "No supported claims, wrong version, ambiguous scope or "
        "insufficient calibrated evidence produces `not found`.",
        "- `.cache/phase6/generation/` keys include model, full request/prompt hash, question "
        "ID and context hash. Successful raw completions retain usage/latency/cost; errors "
        "and incomplete/truncated streams are never cached. Reruns reuse successful calls.",
        "- Serving imports no evaluation cache. `RAG_GENERATION_BACKEND=deepseek-flash` "
        "selects the fixed provider; extractive remains default. Serving loads the frozen "
        "calibration in `configs/phase6_calibration.json`, not the evaluation cache.",
        "- Provider SSE is consumed incrementally, but user-visible output is buffered until "
        "verification completes; JSON and SSE responses expose the same final claims, "
        "citations, answered_version and abstention state.",
        "",
        "## Limitations",
        "",
        "- Correctness is lexical matching to the gold answer; paraphrases can be marked "
        "wrong and long extracts can match incidentally. Faithfulness is lexical support, "
        "not semantic entailment. Citation precision is exact quote/identity/version validity, "
        "not a human relevance judgment. High scores do not establish factual correctness.",
        "- Gold is mostly model-written/model-audited; only four human-reviewed references "
        "are available. No new manual annotation or independent semantic judge was obtained.",
        "- Abstentions have no faithfulness/citation observation. Read answered coverage "
        "alongside those conditional metrics. Small correlated cohorts yield wide intervals.",
        "- Verified lexical support is enforced by construction, so a support score of 1.0 "
        "is an internal consistency check, not independent evidence of semantic faithfulness.",
        "- Explicit version scoping is supplied as request metadata; this run does not test "
        "automatic version selection. Public PostgreSQL text uses simulated ACL restrictions.",
        "- The provider alias is mutable; cache entries pin the model ID, prompt and context, "
        "not the provider's hidden weight revision. Token cost excludes failed-attempt charges "
        "if the provider omits usage. Actual billing is unverified.",
        "",
    ]
    return "\n".join(table), "\n".join(lines)


async def run() -> None:
    started = time.perf_counter()
    rows = [
        json.loads(line)
        for line in (ROOT / "data/eval/gold.jsonl").read_text().splitlines()
        if line.strip()
    ]
    if Counter(r["split"] for r in rows) != {"dev": 115, "test": 97}:
        raise ValueError("expected frozen dev=115/test=97")
    if any(not r["validated"] or r["review_status"] != "accepted" for r in rows):
        raise ValueError("unvalidated gold")
    manifest = freeze_subset(rows, ROOT / "data/eval/phase6_subset.json")
    dev = sorted((r for r in rows if r["split"] == "dev"), key=lambda r: r["id"])
    test = sorted((r for r in rows if r["id"] in manifest["ids"]), key=lambda r: r["id"])
    print("Frozen 60 test IDs; initializing read-only Phase 5 retrieval snapshot", flush=True)
    snapshot = RetrievalSnapshot()
    cache = EvaluationCache(ROOT / ".cache/phase6")
    llm = OpenAICompatibleGenerator(verified=False)
    extractive = ExtractiveAnswerGenerator()
    raw: dict[str, list[tuple[dict[str, Any], GenerationRequest, GeneratedAnswer, float]]] = {
        "extractive": [],
        "llm": [],
    }
    cache_hits = 0
    calls = 0
    for split, cohort in (("dev", dev), ("test", test)):
        for i, row in enumerate(cohort, 1):
            request = snapshot.retrieve(row)
            local_start = time.perf_counter()
            baseline = await extractive.generate(request)
            baseline = replace(
                baseline, answered_version=None if baseline.abstained else request.answered_version
            )
            local_seconds = time.perf_counter() - local_start
            raw["extractive"].append((row, request, baseline, local_seconds))
            llm_start = time.perf_counter()
            if request.matches:
                try:
                    answer, hit = await cache.generate(llm, request, row["id"])
                except Exception as exc:
                    print(
                        f"FAIL {split} [{i}/{len(cohort)}] {row['id']}: "
                        f"{type(exc).__name__}: {exc}",
                        flush=True,
                    )
                    raise
                cache_hits += int(hit)
                calls += int(not hit and "usage" in answer.metadata)
                source = "hit" if hit else "miss"
            else:
                answer, source = abstention(reason="policy_denied_or_empty_scope"), "local/no-call"
            raw["llm"].append((row, request, answer, time.perf_counter() - llm_start))
            print(
                f"{split} [{i}/{len(cohort)}] {row['id']} elapsed="
                f"{time.perf_counter() - started:.1f}s cache={source} "
                f"authorized_chunks={len(request.matches)} abstained={answer.abstained}",
                flush=True,
            )
        if split == "dev":
            calibration = {
                name: calibrate([(r, q, a) for r, q, a, _ in items]) for name, items in raw.items()
            }
            atomic_json(
                ROOT / "configs/phase6_calibration.json",
                {
                    "model": MODEL,
                    "gold_hash": manifest["gold_hash"],
                    "calibration": calibration,
                    "prompt_hash": digest(llm.payload(GenerationRequest("calibration", ()))),
                },
            )
            print(
                "Dev calibration frozen: "
                + json.dumps({k: v["threshold"] for k, v in calibration.items()}),
                flush=True,
            )
    scored: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    for name, items in raw.items():
        raw_arm = "extractive" if name == "extractive" else "llm-unverified"
        verified_arm = "extractive-verified" if name == "extractive" else "llm-verified"
        for row, request, answer, seconds in items:
            marked = annotate(answer, request)
            verified_start = time.perf_counter()
            verified = verify_answer(answer, request, threshold=calibration[name]["threshold"])
            verification_seconds = time.perf_counter() - verified_start
            scored[raw_arm].append(scored_record(row, request, marked, raw_arm, seconds))
            scored[verified_arm].append(
                scored_record(
                    row,
                    request,
                    verified,
                    verified_arm,
                    seconds + verification_seconds,
                )
            )
    dev_summaries = {
        arm: summarize([r for r in items if r["split"] == "dev"]) for arm, items in scored.items()
    }
    test_summaries = {
        arm: summarize([r for r in items if r["split"] == "test"]) for arm, items in scored.items()
    }
    human = {
        arm: summarize([r for r in items if r["review_method"] == "human"])
        for arm, items in scored.items()
    }
    x, y = dev_summaries["extractive-verified"], dev_summaries["llm-verified"]
    dev_llm = [a for r, _, a, _ in raw["llm"] if r["split"] == "dev" and "usage" in a.metadata]
    all_llm = [a for _, _, a, _ in raw["llm"] if "usage" in a.metadata]

    def costs(answers: list[GeneratedAnswer], bound: str) -> float:
        return sum(a.metadata["cost"][f"estimated_usd_{bound}"] for a in answers)

    decision = {
        "selected": "deepseek-flash-verified"
        if (
            y["correctness"]["mean"] >= x["correctness"]["mean"] + 0.02
            and y["wrong_version_answers"]["mean"] <= x["wrong_version_answers"]["mean"]
        )
        else "extractive-verified",
        "extractive_correctness": x["correctness"]["mean"],
        "llm_correctness": y["correctness"]["mean"],
        "extractive_median_seconds": statistics.median(
            t for r, _, _, t in raw["extractive"] if r["split"] == "dev"
        ),
        "llm_median_seconds": statistics.median(a.metadata["latency_seconds"] for a in dev_llm),
        "cost_lower_usd": costs(dev_llm, "lower"),
        "cost_upper_usd": costs(dev_llm, "upper"),
    }
    result = {
        "phase": 6,
        "model": MODEL,
        "endpoint": ENDPOINT,
        "stream": True,
        "thinking": "disabled",
        "temperature": 0,
        "calibration": calibration,
        "subset": manifest,
        "subset_counts": subset_counts(test),
        "retrieval": snapshot.provenance,
        "dev_decision": decision,
        "dev_summaries": dev_summaries,
        "test_summaries": test_summaries,
        "human_alignment": human,
        "rows": scored,
        "metric_definitions": {
            "correctness": "lexical phrase/guarded token overlap; proxy, not human scoring",
            "faithfulness": "supported included claims / included claims, excluding abstentions",
            "citation_precision": "exact quote/identity/requested-version validity, not relevance",
            "abstention_correctness": "matches not answerability OR not acl_allowance",
            "wrong_version_answers": "answered version/citations disagree with requested version",
        },
        "usage": {
            "calls": len(all_llm),
            "new_calls": calls,
            "cache_hits": cache_hits,
            "prompt_tokens": sum(a.metadata["usage"]["prompt_tokens"] for a in all_llm),
            "completion_tokens": sum(a.metadata["usage"]["completion_tokens"] for a in all_llm),
            "cost_lower_usd": costs(all_llm, "lower"),
            "cost_upper_usd": costs(all_llm, "upper"),
        },
        "elapsed_seconds": time.perf_counter() - started,
        "code_hashes": {
            str(p.relative_to(ROOT)): fingerprint_file(p)
            for p in [
                Path(__file__).resolve(),
                *sorted((ROOT / "src/rag_service/generation").glob("*.py")),
                ROOT / "src/rag_service/evaluation/phase6.py",
            ]
        },
    }
    result_path = ROOT / "results/phase6_results.json"
    history = []
    if result_path.exists():
        previous = json.loads(result_path.read_text(encoding="utf-8"))
        if previous.get("subset") == manifest and previous.get("model") == MODEL:
            history = previous.get(
                "execution_history",
                [
                    {
                        "elapsed_seconds": previous["elapsed_seconds"],
                        "new_calls": previous["usage"]["new_calls"],
                        "cache_hits": previous["usage"]["cache_hits"],
                    }
                ],
            )
    result["execution_history"] = [
        *history,
        {
            "elapsed_seconds": result["elapsed_seconds"],
            "new_calls": calls,
            "cache_hits": cache_hits,
        },
    ]
    atomic_json(ROOT / "results/phase6_results.json", result)
    table, findings = reports(result)
    (ROOT / "results/phase6_table.md").write_text(table, encoding="utf-8")
    (ROOT / "docs/phase6_findings.md").write_text(findings, encoding="utf-8")
    print(
        f"Phase 6 complete in {result['elapsed_seconds']:.1f}s; "
        f"new_calls={calls}, cache_hits={cache_hits}",
        flush=True,
    )


if __name__ == "__main__":
    asyncio.run(run())
