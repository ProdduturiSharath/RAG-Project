# Phase 6 findings

Generated from `results/phase6_results.json`.

## Protocol

- Provider: `https://api.deepseek.com/chat/completions`; model `deepseek-flash` only.
- `temperature=0`, `stream=true`, `thinking.type=disabled`; 45s total deadline per HTTP attempt, at most 3 attempts; 0.5s start throttle, 429/5xx exponential backoff.
- JSON answers include answered_version, atomic claims, exact document/version/section/chunk identifiers and verbatim quotes. Raw reasoning is neither requested nor stored.
- All 115 dev rows calibrate separate extractive and LLM abstention thresholds. Threshold selection maximizes balanced answerable/should-abstain decision accuracy; test outcomes never select a threshold, prompt, subset, or retrieval arm.
- Thresholds: extractive=0.00; LLM=0.00.
- The 60 test IDs are frozen in `data/eval/phase6_subset.json` before generation, stratified by type, retaining every negative and both human-reviewed test rows.
- Test type counts: `{"acl": 4, "exact_identifier": 10, "factoid": 10, "multi_hop": 2, "table": 5, "unanswerable": 4, "unchanged_control": 6, "version_specific": 11, "version_unavailable": 8}`.
- Reuses the Phase 5 BGE-small query vectors, existing Postgres BGE-small corpus vectors, cached BM25 and vectorized scoring; weighted alpha=0.5, top 5, explicit requested target_version. No training or GPU stage is run. Database reads only.
- Four arms share identical authorized/scoped context. The two LLM arms share one raw completion per question; verification is entirely local.
- ACL cohorts request the simulated restricted collection. Policy denies 8 requesters (5 dev, 3 selected test), which abstain without provider access. Actual private corpora fail preflight. No unauthorized chunks are sent.

## Test results

| Arm | Correctness* | Faithfulness* | Citation precision* | Abstention correctness | Wrong-version answers | Answered |
| --- | --- | --- | --- | --- | --- | ---: |
| extractive | 0.283 [0.188, 0.424] | 0.243 [0.185, 0.314] | 1.000 [1.000, 1.000] | 0.800 [0.646, 1.000] | 0.000 [0.000, 0.000] | 57 |
| extractive-verified | 0.317 [0.100, 0.493] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.667 [0.542, 0.771] | 0.000 [0.000, 0.000] | 25 |
| llm-unverified | 0.617 [0.436, 0.754] | 0.876 [0.743, 0.970] | 1.000 [1.000, 1.000] | 0.900 [0.769, 1.000] | 0.000 [0.000, 0.000] | 39 |
| llm-verified | 0.517 [0.278, 0.673] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.767 [0.522, 0.912] | 0.000 [0.000, 0.000] | 31 |

*Deterministic lexical-reference / quote-support proxies, not human semantic judgments. Faithfulness and citation precision exclude abstentions.
Wrong-version rate uses all 60 questions as denominator. CIs resample lineage clusters (2,000 draws, seed 42).

Verification trades coverage for lexical support: compare the answered count and correctness with the unverified arm; a higher conditional support score alone is not an answer-quality improvement.

## Dev model / cost decision

- Decision: **deepseek-flash-verified**. Rule: prefer verified LLM only if dev correctness proxy gains at least 0.02 and wrong-version rate does not increase.
- Dev verified correctness: extractive=0.226, LLM=0.409.
- Dev median generation latency: extractive=0.0015s, LLM=1.406s (provider-recorded latency, including retries).
- Dev LLM token-cost estimate: $0.046303–$0.092607; extractive API cost $0.
- All dev+test successful LLM responses: 167; token-cost estimate $0.069812–$0.139625. Billed dollars / granted balance are unknown.
- Rates from https://api-docs.deepseek.com/quick_start/pricing: per million tokens $0.003–0.006 input cache-hit, $0.15–0.30 input cache-miss, $0.60–1.20 output. Do not interpret the estimate as proof of free-tier usage.

## Human-reviewed alignment

The existing four human-reviewed gold rows (2 dev, 2 test) are evaluated separately. These are reference-answer alignments, not newly collected human ratings of generated answers and not an LLM-judge agreement study.
- extractive: n=4, correctness proxy 0.750 [0.500, 1.000].
- extractive-verified: n=4, correctness proxy 0.250 [0.000, 0.500].
- llm-unverified: n=4, correctness proxy 1.000 [1.000, 1.000].
- llm-verified: n=4, correctness proxy 0.500 [0.000, 1.000].

## Verification, cache and serving

- Exact quotes and document/version/section/chunk identity must match transmitted authorized evidence. Claim support uses token overlap plus numeric, identifier and negation guards. Unsupported claims are stripped from answer text and retained as flagged claim diagnostics (`included=false`); faithfulness scores only delivered claims. No supported claims, wrong version, ambiguous scope or insufficient calibrated evidence produces `not found`.
- `.cache/phase6/generation/` keys include model, full request/prompt hash, question ID and context hash. Successful raw completions retain usage/latency/cost; errors and incomplete/truncated streams are never cached. Reruns reuse successful calls.
- Serving imports no evaluation cache. `RAG_GENERATION_BACKEND=deepseek-flash` selects the fixed provider; extractive remains default. Serving loads the frozen calibration in `configs/phase6_calibration.json`, not the evaluation cache.
- Provider SSE is consumed incrementally, but user-visible output is buffered until verification completes; JSON and SSE responses expose the same final claims, citations, answered_version and abstention state.

## Limitations

- Correctness is lexical matching to the gold answer; paraphrases can be marked wrong and long extracts can match incidentally. Faithfulness is lexical support, not semantic entailment. Citation precision is exact quote/identity/version validity, not a human relevance judgment. High scores do not establish factual correctness.
- Gold is mostly model-written/model-audited; only four human-reviewed references are available. No new manual annotation or independent semantic judge was obtained.
- Abstentions have no faithfulness/citation observation. Read answered coverage alongside those conditional metrics. Small correlated cohorts yield wide intervals.
- Verified lexical support is enforced by construction, so a support score of 1.0 is an internal consistency check, not independent evidence of semantic faithfulness.
- Explicit version scoping is supplied as request metadata; this run does not test automatic version selection. Public PostgreSQL text uses simulated ACL restrictions.
- The provider alias is mutable; cache entries pin the model ID, prompt and context, not the provider's hidden weight revision. Token cost excludes failed-attempt charges if the provider omits usage. Actual billing is unverified.
