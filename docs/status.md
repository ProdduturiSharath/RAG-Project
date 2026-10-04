# Phase 0 status

## Baseline before Phase 0 edits

Baseline branch: `phase-0-audit-foundation`.

The baseline was run after creating `.venv` and installing the repository's
existing `.[dev]` extra plus `mypy` manually. It was run before the Phase 0
configuration and audit edits.

### Test command

```text
$ .venv/bin/python -m pytest -q
........                                                                 [100%]
=============================== warnings summary ===============================
tests/unit/test_evaluation.py::EvaluationTests::test_retrieval_metrics_make_misses_visible
  .../pytest_asyncio/plugin.py:1216: DeprecationWarning: 'asyncio.get_event_loop_policy' is deprecated and scheduled for removal in Python 3.16
1 warning in 0.11s
8 passed, 1 warning in 0.11s
```

### Lint command

```text
$ .venv/bin/ruff check src tests
All checks passed!
```

### Type-check command

```text
$ .venv/bin/mypy src tests
tests/unit/test_provider_adapters.py:65: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:66: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:71: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:72: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:73: error: Value of type "None" is not indexable  [index]
tests/unit/test_evaluation.py:20: error: Argument 2 to "EvaluationCase" has incompatible type "set[str]"; expected "frozenset[str]"  [arg-type]
Found 6 errors in 2 files (checked 36 source files)
```

The baseline test and lint results are command output, not retrieval or answer
metrics. No benchmark result exists in this baseline.

## Installed tool versions at baseline

The source command was `.venv/bin/python -m pip show pytest ruff mypy fastapi
pydantic`. The observed versions were pytest 8.4.2, Ruff 0.16.10, mypy 2.4.0,
FastAPI 0.142.2, and Pydantic 2.13.5. The lock file is the reproducible source
for the complete environment.

## Phase 0 completion checks

These are filled after the audit edits and mutation runs:

- [x] typed settings and experiment provenance pass
- [x] all tests pass
- [x] Ruff passes
- [x] mypy passes
- [x] README claim audit is committed
- [x] module inventory is committed
- [x] ACL mutants are caught by named tests
- [x] mutation tool availability is recorded
- [x] no benchmark metrics were invented

## ACL hand-mutant results

Each mutant was applied directly to the working tree, run against the named
target, and restored before proceeding. Every mutant was caught:

| Mutant | Command | Result |
| --- | --- | --- |
| Apply ACL filtering after the candidate limit | `.venv/bin/python -m pytest tests/unit/test_retrieval.py -q` | **Caught** by `test_acl_filtering_precedes_candidate_limit`: `1 failed, 3 passed`; the expected public result was empty after the bad top-1 restricted candidate. |
| Drop group authorization | `.venv/bin/python -m pytest tests/unit/test_retrieval.py::RetrievalTests::test_group_acl_is_checked_for_denied_and_allowed_groups -q` | **Caught**: `1 failed`; the allowed `operations` group returned no result. |
| Ignore principal identity | `.venv/bin/python -m pytest tests/unit/test_retrieval.py::RetrievalTests::test_document_acl_is_applied_before_ranking -q` | **Caught**: `1 failed`; `restricted` unexpectedly appeared for `bob`. |

`mutmut` is not installed in this environment: `.venv/bin/python -m mutmut
--version` returned `No module named mutmut`. Phase 0 therefore uses the
required hand-written mutants under WSL2. No mutant was left in the final tree.

## Phase 0 result artifact

The committed foundation CLI produced:

```text
$ .venv/bin/python -m rag_service.evaluation.run --config configs/phase-0-foundation.yaml
results/f53cf6e8a31fa0261e124451b1ab0a246c98447880e01300d04a224fbada28f6.json
```

This artifact has an empty `metrics` object because Phase 0 has no dataset or
benchmark. It records the config hash, seed, library versions, and hardware;
it does not invent a retrieval metric.

## Things I am unsure about

- Google AI Studio's current OpenAI-compatible endpoint, fixed Flash/Flash-Lite
  model availability, free-tier limits, and model terms could not be verified
  because the official AI documentation returned HTTP 429 in this environment.
- The current repository's Pinecone adapter is only tested against a fake client;
  no live provider behavior is claimed.
- The project has no corpus or validated benchmark, so no retrieval quality
  conclusion is warranted.

## Phase 1 post-PR-2 handoff — 2026-10-03

- PR #2 remains open and unmerged on `phase-1-postgres-versioned-ingestion`.
- Commits `a4bbf47`, `2cd61e9`, and `c0f594a` add disposable integration
  databases, atomic-revision/reader/concurrency coverage, pinned pgvector CI,
  localhost-only Compose binding, `.env` password configuration, and typed HTML
  table/code parsing.
- The two required hand mutants were each caught and restored: omitted
  supersession failed the reader atomicity test; omitted
  `document_versions_one_active` failed the unique-index test.
- Final local verification: full suite `28 passed`; integration suite `13
  passed`; Ruff and mypy passed. CI run `37120488480` passed both unit and
  integration jobs; its integration job created and dropped a `rag_test_*`
  database and reported `13 passed`.
- Clean-volume Compose restart was run twice during verification; the final
  suite was run twice in sequence and once with a seeded shuffled order.
- Live query verified PostgreSQL `17.11` with pgvector `0.8.7`; the exact
  official release URL checked was
  `https://github.com/pgvector/pgvector/releases/tag/v0.8.7`.
- Real smoke input was fetched to `/tmp/omnirush` only from PostgreSQL 17
  documentation; it produced 125 sections, 2 table chunks, and 2 code chunks.

Phase 2 implementation is complete on `phase-2-retrieval-pipeline`; final verification and PR are recorded in `docs/phase-2-report.md`.

## Phase 3 Postgres follow-up — 2026-10-04

- Postgres container `evidence-rag-postgres-1` was healthy; API and worker were
  intentionally left stopped. The separate `evidence_rag_eval` database was
  created and used for corpus ingestion.
- The table audit found 460 literal SGML table elements containing cells in
  PostgreSQL 15 and 459 parser table records/chunks. The one literal omission
  is an XSLT/HTML table inside `func.sgml` line 15106 within a code example,
  not a documentation table. The parser previously lost titled real tables;
  title-state handling was fixed and covered by a real SGML-table test.
- `scripts/corpus_metrics.py` now reports: pg-15 `7893 sections / 10741
  chunks / 459 tables / 3822 code`; pg-16 `7984 / 10877 / 467 / 3873`; pg-17
  `8069 / 10997 / 463 / 3939`.
- Eval ingestion used `bge-small-en-v1.5`: pg-15 computed 10,653 and reused
  0 embeddings in 1,135.776 seconds; pg-16 computed 1,431 and reused 9,356
  in 187.740 seconds; pg-17 computed 1,457 and reused 9,447 in 197.899
  seconds. Total embedding time was 1,521.415 seconds; artifact:
  `data/eval/ingestion_metrics.json`.
- Full suite with the disposable test database: `48 passed in 48.06s`.
  The earlier 16 skips were the 4 Postgres retrieval tests, 3 schema/job
  tests, 4 revision-atomicity tests, and 5 versioned-storage contract tests;
  all now pass. PR #4 remains open; unit and integration CI both pass.

## Phase 3 manual drafting checkpoint — 2026-10-04

This checkpoint supersedes the generated-candidate counts in the original
Phase 3 report. Branch: `phase-3-corpus-benchmark`. PR #4 has not been merged;
Phase 4 has not started. The NVIDIA API is dropped. No external API was called
and `.env` was not read. Drafting rules are saved in
`docs/question-drafting-rules.md`; read those before continuing.

### Corrected corpus refresh

- Source records: pg-15 **7,893**, pg-16 **7,984**, pg-17 **8,069**; total
  **23,946**, spanning **12,581** current lineage keys.
- Preserved **11,247** surviving assignments; assigned **1,334** new keys
  deterministically without adding blind keys. Of **662** retired keys,
  **62** retired blind keys remain reserved, keeping the original pool intact.
- Persisted split counts: train **3,814**, dev **3,808**, test **3,806**,
  blind **1,215** (12,643 assignments including the 62 retired blind keys).
- Re-mined **732** changed lineage/version pairs from **11,365** adjacent-version
  matches. Change counts: defaults **3**, parameter additions **182**, removals
  **90**, rename hints **9**, table rows added **262**, removed **186**, other
  text changes **546**. No questions were based on other text changes.
- Fixed default-change attribution: a nearby `shared_buffers` reference no
  longer steals `vacuum_buffer_usage_limit`'s default change.
- The **3 lineage tests** passed during refresh. Final audit also compared
  surviving assignments, the complete blind pool, and every saved blind passage
  against pre-session commit `45a586d`: all unchanged.
- Full corrected sources are local/ignored at
  `data/processed/source_sections.full.jsonl`. The committed compact source
  artifact contains **1,253** records, including the untouched blind passages.

### Completed batches and counts

All questions were written directly by `omnirush/gpt-6-astra` after reading
eligible passages. No question generator, template, external model, retrieval
code, or retrieval results were used for drafting. The old **198** generated
candidates and their generator were removed.

| Batch | Accepted | Discarded | Contents |
| --- | ---: | ---: | --- |
| `batch_001.json` | 25 | 0 | 12 version-specific, 5 controls, 8 unavailable |
| `batch_002.json` | 25 | 0 | 8 factoid, 8 identifier, 5 table, 2 multi-hop, 2 ACL |
| `batch_003.json` | 25 | 0 | 18 unanswerable, 6 ACL, 1 table |
| `batch_004.json` | 25 | 0 | 13 factoid, 12 identifier |
| `batch_005.json` | 25 | 0 | 14 factoid, 11 identifier |
| `batch_006.json` | 24 | 1 | 19 table, 4 identifier, 1 unavailable |

The rejected batch-006 row asked about `scram_iterations` in PostgreSQL 15:
the identifier occurs in that version's full corpus, so it cannot pass the
strict version-unavailable check. The raw draft remains in the batch for audit;
it is absent from candidates. Each batch has a `.report.json` with reasons.

| Type | Accepted | Discarded | Target | Remaining |
| --- | ---: | ---: | ---: | ---: |
| factoid | 35 | 0 | 35 | 0 |
| exact_identifier | 35 | 0 | 35 | 0 |
| table | 25 | 0 | 25 | 0 |
| multi_hop | 2 | 0 | 12 | 10 |
| unanswerable | 18 | 0 | 18 | 0 |
| acl | 8 | 0 | 8 | 0 |
| version_specific | 12 | 0 | up to 50 | up to 38 |
| unchanged_control | 5 | 0 | 25 | 20 |
| version_unavailable | 9 | 1 | 10 | 1 |

**149 accepted, 1 discarded.** Target versions are pg-15 **50**, pg-16 **45**,
pg-17 **54**. Factoid and identifier each have **17/35** paraphrased rows.
All accepted rows have `author=llm_drafted`, `drafted_by=omnirush/gpt-6-astra`,
and `validated=false`. Stable-source categories use `version_independent=true`.
These are unreviewed candidates, not a validated benchmark.

### Resume exactly here

Stopped at a context checkpoint after completing **batches 001–006**; those
batches were committed individually and pushed after batches 003 and 006.
**Next batch: `data/eval/drafts/batch_007.json`.** Remaining work is **10
multi-hop**, **20 unchanged controls**, **1 version-unavailable**, and **up to
38 version-specific** questions. No remaining source-scarcity claim has been
made: the specialized diff pool has not been exhausted. Manually screen mined
identifier additions/removals against full sources; a mention or table-position
change does not establish a feature's introduction/removal.

Do not re-import completed batches (the importer will discard duplicates).
Use the persisted split file. Do not regenerate candidates or touch the blind
pool. For new batches:

```bash
PYTHONPATH=src .venv/bin/python scripts/inspect_drafting_sources.py --help
PYTHONPATH=src .venv/bin/python scripts/import_drafts.py data/eval/drafts/batch_007.json
PYTHONPATH=src .venv/bin/python scripts/audit_drafts.py
```

### Verification at this checkpoint

- Importer checks normalized-whitespace quote matching and persists original
  quotes plus exact character offsets, full-source identifier absence, dev/test
  membership for every evidence section, stable-lineage claims, specialized
  diff provenance, distinct same-version multi-hop sources, ACL source/requester
  membership, duplicate questions, and common placeholder/vague/meta wording.
- Final audit rechecked **all 149 accepted rows** against all three full local
  versions. Summary: `data/eval/drafting_stats.json`.
- Importer tests: **13** tests included in the final suite. Full suite was run
  **once at the end: 63 passed in 9.58s**, including the disposable PostgreSQL
  database tests, with no skips. `.env` loading was explicitly disabled before
  pytest collection; offline model flags prevented model downloads:

```bash
RAG_TEST_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres \
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -c \
"from rag_service.settings import Settings; Settings.model_config['env_file'] = None; import pytest; raise SystemExit(pytest.main(['-q']))"
```

- Ruff (`src tests scripts`) and mypy (`src tests`) pass. Dataset validation
  passes with no errors and four target-shortfall warnings; partial pools are
  allowed. The importer and schema never mark model-authored drafts validated.
- **Current PR #4 CI is unverified.** Querying GitHub checks would call an
  external API, prohibited by this session's instructions. The historical green
  status above applies to the previous commit, not this checkpoint. Local checks
  pass; a future session with permission to query GitHub must check the new SHA.

### Labeling commands

```bash
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py review --candidates data/eval/candidates.jsonl --output data/eval/reviewed.jsonl
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py write --source data/eval/source_sections.jsonl --splits data/eval/splits.json --output data/eval/blind.jsonl
```
