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
