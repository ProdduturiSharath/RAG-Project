# Phase 2 report — retrieval pipeline

## 1. What was implemented

Phase 2 is implemented on `phase-2-retrieval-pipeline`.

- Rebuilt the local environment on Python 3.12.15 and pinned CPU PyTorch,
  sentence-transformers, Transformers, and model-runtime dependencies.
- Added lazy local BGE small/base dense adapters and the configurable metadata
  prefix switch. BGE model cards were checked for MIT licensing.
- Added Postgres full-text and identifier search, a true Okapi BM25 baseline,
  identifier-aware tokenization, RRF/normalized weighted fusion, and a lazy
  Apache-2.0 MiniLM cross-encoder with token-overlap retained as baseline.
- Added typed scope/auth, dense, sparse, fusion, rerank, parent/context, and
  trace stages. Scope supports none, explicit exact/latest/all, and auto with
  an explicit ambiguous result.
- Added HNSW/identifier GIN migrations, iterative HNSW scans, citations with
  document/product version/revision/section path, API trace/scope fields, and
  persisted per-stage query traces.
- Fixed one-column HTML command-output parsing so `wal_level` remains data
  rather than becoming a fabricated header row.
- Added Postgres denied-group and allowed-group integration tests. The adapter
  group predicate was already correct; the earlier failure was isolated by the
  disposable database fixture and was not a production adapter gap.

## 2. Commands and actual output

```text
$ .venv/bin/python -c 'import torch, sentence_transformers; ...'
{'torch': '2.14.1+cpu', 'sentence_transformers': '6.1.0',
 'embedding_shape': (1, 384), 'reranker_scores': [7.242594242095947]}

$ RAG_TEST_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/postgres' \
  .venv/bin/python -m pytest -q -s
42 passed in 65.51s (0:01:05)

$ .venv/bin/ruff check src tests
All checks passed!

$ .venv/bin/mypy src tests
Success: no issues found in 57 source files
```

## 3. Test and contract results

The final suite includes 8 retrieval-pipeline unit tests, 3 provider-adapter
tests, 2 citation/generation tests, parser regression coverage, Postgres group
ACL coverage, version-scope removal-sensitive coverage, staged Postgres search,
trace persistence, and index migration checks. ACL and version tests assert the
authorized group/version result directly, so removing either SQL filter fails.

## 4. Metrics and results

No benchmark retrieval metrics were produced because the corpus and validated
Phase 3 benchmark do not exist yet. The full-suite timing above is verification
telemetry, not a retrieval-quality claim. No new `results/<hash>.json` artifact
was created.

## 5. Sources and deviations

- BGE small: <https://huggingface.co/BAAI/bge-small-en-v1.5>
- BGE base: <https://huggingface.co/BAAI/bge-base-en-v1.5>
- Cross-encoder: <https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2>
- pgvector 0.8.7 README: <https://raw.githubusercontent.com/pgvector/pgvector/v0.8.7/README.md>

The legacy hash, in-memory, token-overlap, and extractive adapters remain named
baselines. The synchronous compatibility method remains available; FastAPI and
the normal asynchronous path use the full traced staged pipeline.

## 6. Things I am unsure about

- BGE and cross-encoder weights are downloaded from Hugging Face at first use;
  CI exercises the local adapters, but no model weights are committed.
- Approximate HNSW recall still requires the Phase 3 corpus and benchmark.

## 7. Abstractions or code that should be removed

The Phase 1 Pinecone adapter should be reconsidered only after Phase 3 measures
a real provider need.
