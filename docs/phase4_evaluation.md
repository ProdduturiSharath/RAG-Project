# Phase 4 evaluation

Run `bash scripts/run_phase4.sh` from a checkout with the host `.venv` and the
repaired Phase 3 corpus in `evidence_rag_eval` at `127.0.0.1:5432`.
The runner does not load `.env`. Set `RAG_EVAL_DATABASE_URL` in the terminal if
the default local `postgres:postgres` credentials differ. Results are resumable,
fingerprinted, and written under `results/`; logs append to `results/phase4.log`.

## Official BGE finding (checked 2026-10-10)

The [BAAI model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
([raw card](https://huggingface.co/BAAI/bge-small-en-v1.5/raw/main/README.md))
recommends `Represent this sentence for searching relevant passages: `
(including the trailing space) for short-query/long-passage retrieval.
It says v1.5 also works without instructions, usually with slight degradation,
and recommends choosing the setting using task performance. Passages receive
no query instruction. `SentenceTransformerEncoder.embed_query` already added
this exact prefix unconditionally before Phase 4. It now has a boolean
`query_instruction` switch (application environment: `RAG_QUERY_INSTRUCTION`),
default **on**, with both hybrid and pure-dense on/off comparisons.

## Protocol

- Gold is the frozen 212-row dev/test artifact. No blind question file is opened.
  Preflight checks schema, accepted review status, evidence/source validation,
  reproducibility from committed review inputs, and 32,719 active corpus chunks
  (10,777 / 10,912 / 11,030 for pg-15 / pg-16 / pg-17), including BGE embeddings.
  The schema's old unconditional ban on validated model drafts is aligned with
  the existing final-gold validator's explicitly accepted `model_audit` exception.
- A hit requires a whole evidence quote after whitespace normalization,
  case preserved, and a valid version: `gold_versions` for independent rows,
  otherwise `target_version`. Lineage is not an additional hit restriction.
- Recall@k is the fraction of distinct evidence quotes covered, averaged over
  questions. Multi-hop also reports all-quotes@k and micro quote coverage.
  MRR uses the first hit in the returned list (30 by default, 60 in that arm).
  nDCG@10 has binary chunk relevance and a full-corpus ideal, so duplicate
  overlapping chunks may be relevant; all-quotes coverage measures hop diversity.
  The ideal uses authorized, version-valid chunks **before version scoping**.
  Questions whose spans fit no indexed chunk score zero and remain in denominators.
- Version confusion@k means any same-lineage wrong version within k ranked
  above the first correct hit. A missing correct hit has rank infinity.
  False exclusion on controls means scoping removes **all** otherwise accessible
  correct chunks; its denominator is controls with at least one such chunk.
- Unanswerable/version-unavailable rows have only top-1 score distributions and
  missing-result counts; no abstention decisions or thresholds are fitted.
- ACL questions use the requester's principal and groups from `data/acl_demo.yaml`.
  Isolated evaluation views partition restricted sections into policy-bearing
  virtual documents, letting the existing SQL ACL predicate run before limits.
  An independent audit checks every candidate stage and expanded parent, and any
  leakage aborts the run. Other question types use the public manual corpus.
- Stage latency is measured by `HybridRetriever` with models warmed before timing;
  total wall time also includes orchestration. Disabled stages are identified.
  Cached results retain their original measurements; initialization is separate.
- Report dev and test separately, type, paraphrased flag, crossed type/flag, and
  review method (including an explicit empty owner-written group). Bootstrap 95%
  percentile intervals use 2,000 draws, seed 42, resampling whole `lineage_key`
  clusters. Paired differences use the same question IDs and lineage draws;
  intervals containing zero are marked **within noise**, not equivalence.

## Systems and host options

`configs/phase-4-evaluation.yaml` is a validated one-setting-at-a-time graph.
The default matches application defaults: BGE-small, instruction on, Postgres
FTS + dense RRF, cross-encoder top-30, parent expansion, no version scope.
Pure retrieval baselines descend through named no-rerank/no-expansion controls;
the parent of every arm is reported. Weighted alpha (0.25/0.5/0.75) and the best
two systems are selected by **dev nDCG@10**, tie-broken by system name, before
test evaluation. Unselected alphas remain dev-only. Failures are the worst
test failures of those two dev-selected systems, up to 30 actual failures each.

Optional flags, all off by default:

- `--metadata-prefix`: re-embed document/version/section-prefixed inputs under
  their own `::metadata-v1` embedder ID and input-text hash (including metadata).
- `--bge-base`: locally embed the same corpus using BGE-base.
- `--chunk-size`: re-chunk saved complete sections at 120 and 440 tokens with
  the existing chunker, fixed 35-token overlap; re-embed new chunk inputs.
- `--scifact`: run the SciFact check **last**, using the same Postgres dense
  stage and query encoder, no reranker or expansion, title + abstract documents.
- `--refresh`: recompute query results; corpus/embedding caches remain reusable.

All model inference is local on the host. The host may download missing model
weights; there are no model API calls. Existing ingestion and public tables are
preserved; content-addressed `phase4_*` schemas hold evaluation snapshots/caches.

The host run also writes `results/phase4_smoke.json`, a 40-question dev cache.
Commit that measured artifact with the results to activate the offline CI replay
gate. Before the first host run the cache-dependent CI step is skipped; no
synthetic retrieval outcomes are substituted for measured ones.

## SciFact reference

The [official BEIR dataset list](https://github.com/beir-cellar/beir#beers-available-datasets)
links the [SciFact archive](https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip)
with MD5 `5f7d1de60b170fc8027bb7898e2efca1`, 300 test queries and about 5K documents.
The BAAI card's `model-index` entry for **MTEB SciFact**, test split, reports
`ndcg_at_10: 71.275`, i.e. **0.71275** on a 0–1 scale. The optional check prints
the measured number beside this published reference, with both URLs. It is a
sanity comparison, not a claim of identical MTEB software/model revisions.

No retrieval measurements have been produced in the sandbox. Host execution is
required before choosing a winning system or making a quality claim.
