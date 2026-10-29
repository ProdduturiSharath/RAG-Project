# Phase 8 packaging findings

## What was delivered

- Root-level disposable PostgreSQL fixture with a separately named maintenance
  URL, exact generated `rag_test_<uuid>` validation, and teardown cleanup.
- Persistent trace metadata for generation mode, latency, abstention, and cost,
  plus authenticated trace and summary endpoints.
- Isolated `evidence_rag_demo` seed using deterministic `hash-v1` vectors and
  extractive generation. The seed refuses to overwrite an existing schema.
- Compose configuration for the dedicated `evidence_rag_demo_pgdata` volume and
  optional Streamlit UI.
- Findings-first UI controls for JWT presets, version scope, generation mode,
  sparse-vs-hybrid comparison, citations, claim support, stage latency, and
  persistent cost summary.
- Isolated ingestion/read-only latency benchmark with JSON and Markdown output.

## Measured results

The final isolated benchmark created and dropped a temporary
`rag_test_phase8_285bedad1f3645b985cc6b6c94182ebf` database:

- 24 documents, 24 versions, 48 chunks, 48 sections, and 24 deterministic
  embedding records.
- Ingestion p50/p95: **174.500 / 178.326 ms**.
- Read-only query p50/p95: **27.367 / 28.967 ms**.
- API cost: **$0.00**.
- Artifact: `results/phase8_results.json`.

## Verification

- Safe full suite: **288 passed** with a fresh disposable `rag_test_<uuid>`
  database created and dropped by the root fixture.
- Ruff: passed.
- Mypy: passed across 102 checked source/test/script files.
- `git diff --check`: pending final closeout after documentation edits.
- The protected database manifest matched before/after for every protected table:
  counts and canonical row SHA-256 values were unchanged in
  `evidence_rag_eval`, `evidence_rag_recovery_20261028`, and the preserved
  recovery schemas.

## Safety and provenance

- No Phase 8 mutation targeted `evidence_rag_eval`,
  `evidence_rag_recovery_20261028`, `public_pre_recovery_20261029`, or any
  `phase4_*`/`phase5_*` schema.
- No PyTorch/SentenceTransformer encoding was used by the safe verification,
  demo seed, or Phase 8 benchmark. The safe test command explicitly used
  `hash-v1` and `token-overlap` adapters.
- No paid external LLM calls were made.
- The recovered evaluation corpus remains 32,719 chunks, 9,083 verified dense
  vectors, 20,756 vector-linked chunks, and 11,963 active chunks without
  verified dense vectors. It remains a reconstruction, not an exact restoration.

## Limitations and deviations

- Docker is unavailable in this environment, so Compose build/startup and browser
  UI smoke testing remain host checks.
- `pg_dump` is installed only at PostgreSQL 15.19 while the server is 17.11;
  no compatible client was available. The canonical manifest is useful for
  change detection but is not equivalent to a logical dump.
- Streamlit is an optional dependency and is not installed in the current
  virtual environment; the UI is syntax/type checked and included in the image
  build path.

## Things I am unsure about

- Local single-process latency is not a production capacity estimate.
- The recovered ACL rows are provenance from surviving Phase 4 artifacts, not
  proof of the lost database's original complete ACL history.
- Demo hash vectors prove deterministic plumbing, not semantic embedding quality.

## Code-removal candidates

- Keep the hash, in-memory, extractive, and token-overlap adapters because they
  are explicit offline/test baselines. Remove an adapter only when its contract
  coverage and documented comparison arm are retired.
- The old Phase 7 artifact fallback was removed; filtered ANN now measures the
  actual public schema.
