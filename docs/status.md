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
