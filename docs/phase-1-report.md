# Phase 1 report — versioned Postgres ingestion

## 1. What was implemented

Phase 1 was implemented on branch `phase-1-postgres-versioned-ingestion` and
pushed to `origin`. The commits are:

| Commit | Work |
| --- | --- |
| `55f3018` | Postgres/pgvector dependency, settings, Compose services, migration foundation, and verified environment record. |
| `50f9f99` | Structured table/code chunks, content hashes, and cross-product-version lineage keys. |
| `cf38040` | Transactional versioned Postgres store, reusable embeddings, ACL storage, Postgres retrieval adapter, jobs, API job/deletion routes, worker, and integration tests. |
| `dd53e3d` | HTML/Markdown parser, explicit no-OCR PDF documentation, and kind-scoped SKIP LOCKED job claiming. |
| `4bcbadb` | Embedder/chunker provenance lifecycle test and pinned pgvector image digest. |

The implementation includes:

- `pgvector/pgvector:pg17` in Docker Compose, pinned to the verified image
  digest.
- SQL migrations in `migrations/` for:
  - `documents`
  - `document_versions` with `building`, `active`, `superseded`, and `deleted`
    states
  - a partial unique index allowing only one active revision per
    `(document_id, product_version)`
  - `sections` with parent links and stable lineage keys
  - typed `text`, `table`, and `code` chunks
  - content-hash/embedder keyed embeddings
  - ACL principals/groups
  - leased jobs and `query_traces`
  - GIN indexing over generated `tsvector` chunk content
- `PostgresVersionedStore` with:
  - content-hash no-op ingestion
  - separate `product_version` and `revision`
  - reusable embeddings across product versions
  - ACL-only updates without re-embedding
  - parser/chunker/embedder provenance hashes
  - transactional revision activation and rollback safety
  - deletion of version chunks and orphaned embedding cache rows
- `InMemoryVersionedStore` as the matching lifecycle contract fixture.
- `PostgresHybridIndex` with SQL-side active-version and ACL filtering before
  candidate scoring.
- `PostgresJobStore` using `FOR UPDATE SKIP LOCKED` and short leases.
- API routes for synchronous ingest, deletion, async job enqueue/status, and
  product-version query filtering.
- A Compose worker at `python -m rag_service.storage.worker`.
- HTML/Markdown parsing and an explicit text-only/no-OCR PyMuPDF path.
- Structure-aware handling that preserves Markdown tables and fenced code
  blocks as whole typed chunks.
- Integration tests covering in-memory and live Postgres lifecycle behavior.

## 2. Commands to verify and actual output

### Gate check

```text
$ docker compose version
Docker Compose version v5.5.1
```

```text
$ docker run hello-world
Hello from Docker!
This message shows that your installation appears to be working correctly.
...
```

### Official pgvector image and database verification

The official pgvector README was reachable at:

- <https://raw.githubusercontent.com/pgvector/pgvector/master/README.md>
- <https://github.com/pgvector/pgvector/releases>
- <https://www.postgresql.org/docs/current/gin.html>

The live image query returned:

```text
postgres_version: 17.11 (Debian 17.11-1.pgdg12+2)
extversion: 0.8.7
hnsw.iterative_scan: off
ivfflat.iterative_scan: off
hnsw.max_scan_tuples: 20000
hnsw.scan_mem_multiplier: 1
ivfflat.max_probes: 32768
```

The direct SQL check created an HNSW index on `vector(2000)` successfully.
The documented approximate-index limits and iterative-scan behavior are
recorded in `docs/environment.md`.

### Compose

```text
$ docker compose up --build -d
Image evidence-rag-api Built
Image evidence-rag-worker Built
Container evidence-rag-postgres-1 Healthy
Container evidence-rag-api-1 Started
Container evidence-rag-worker-1 Started
```

```text
$ docker compose ps
evidence-rag-api-1       Up
evidence-rag-postgres-1  Up (healthy)
evidence-rag-worker-1    Up
```

### Static and test checks

```text
$ .venv/bin/ruff check src tests
All checks passed!
```

```text
$ .venv/bin/mypy src tests
Success: no issues found in 49 source files
```

```text
$ RAG_TEST_DATABASE_URL='postgresql://postgres:postgres@localhost:5432/evidence_rag' \
  .venv/bin/python -m pytest -q
.......................                                                  [100%]
23 passed, 1 warning in 1.25s
```

The warning is the existing `pytest-asyncio` deprecation warning for
`asyncio.get_event_loop_policy`.

### End-to-end synchronous API path

The live API returned revision 1 for ingest, revision 2 after update, and
deleted the two version revisions:

```text
{"document_id":"phase1-demo","version":"pg17","revision":1,"already_ingested":false}
{"document_id":"phase1-demo","version":"pg17","revision":2,"already_ingested":false}
{"document_id":"phase1-demo","product_version":"pg17","deleted":2}
```

The query between update and deletion cited the updated text:

```text
"excerpt":"Set max_wal_senders to 20.","revision":2
```

### End-to-end async worker path

The API returned a queued job, and the worker changed it to:

```json
{
  "status": "succeeded",
  "attempts": 1,
  "result": {
    "revision": 1,
    "chunk_count": 1,
    "document_id": "phase1-final-async",
    "product_version": "pg17",
    "already_ingested": false
  }
}
```

## 3. Test, lint, type-check, and mutation results

### Lifecycle and contract results

The live Postgres integration suite passed the in-memory/Postgres lifecycle
contract, schema/job checks, and ACL/product-version retrieval check. The final
full output was:

```text
23 passed, 1 warning in 1.25s
```

Covered lifecycle cases include no-op ingestion, new revision, deletion,
ACL-only update without re-embedding, same content across product versions,
embedder change, chunker change, and injected failure rollback.

### Required hand-mutation evidence

The mutations were applied only temporarily and restored. The raw pytest
failure lines are retained here rather than summarized only in a table.

#### ACL bypass mutation

Mutation: append `OR TRUE` to the SQL ACL predicate. Raw output:

```text
FAILED tests/integration/test_postgres_retrieval.py::PostgresRetrievalTests::test_acl_and_product_version_are_filtered_before_ranking
E       AssertionError: Items in the first set but not the second:
E       'pg17'
1 failed, 1 warning in 0.15s
```

This caught unauthorized `pg17` evidence for requester `bob`.

An earlier equivalent ACL mutation that removed the ACL placeholders entirely
was also caught by the database adapter before results were returned:

```text
FAILED tests/integration/test_postgres_retrieval.py::PostgresRetrievalTests::test_acl_and_product_version_are_filtered_before_ranking
E           psycopg.ProgrammingError: the query has 5 placeholders but 7 parameters were passed
1 failed, 1 warning in 0.14s
```

#### Product-version bypass mutation

Mutation: append `OR TRUE` to the requested product-version predicate. Raw
output:

```text
FAILED tests/integration/test_postgres_retrieval.py::PostgresRetrievalTests::test_acl_and_product_version_are_filtered_before_ranking
E       AssertionError: Items in the first set but not the second:
E       'pg16'
1 failed, 1 warning in 0.17s
```

This caught a `pg16` result in an exact `pg17` query.

#### Failure recovery check

The injected mid-ingest failure is asserted by the lifecycle test and the old
active revision remains visible. No failure survived the final suite.

#### Test-isolation failure found during development

The first version of the ACL integration assertion queried a shared database
without a document filter and was correctly rejected by its own broad
expectation:

```text
FAILED tests/integration/test_postgres_retrieval.py::PostgresRetrievalTests::test_acl_and_product_version_are_filtered_before_ranking
E       AssertionError: Items in the first set but not the second:
E       'pg17'
```

The test was fixed to scope the request to its generated `document_id`; the
production ACL predicate did not require a change.

#### Job-claim failure found during development

The initial job contract test used a generic `test` job while the running
worker claimed all kinds. Raw output:

```text
FAILED tests/integration/test_postgres_schema_jobs.py::PostgresSchemaAndJobTests::test_jobs_are_claimed_and_leased
E       AssertionError: unexpectedly None
1 failed, 6 passed, 1 warning in 0.55s
```

The worker now claims only `ingest_document`; generic queue contract jobs are
isolated, and the exact test passes.

Mutation result: ACL bypass and product-version bypass were both caught; no
surviving mutation was observed.

## 4. Metrics produced

No retrieval benchmark metrics were produced in Phase 1. There is no Phase 1
dataset, so no Recall, MRR, latency, cost, or other benchmark number was
invented. No new `results/<hash>.json` metric artifact was created.

The existing Phase 0 provenance-only artifact remains:

- `results/f53cf6e8a31fa0261e124451b1ab0a246c98447880e01300d04a224fbada28f6.json`

Its `metrics` object is empty by design.

## 5. Deviations from the plan and why

- The Phase 1 Postgres retrieval adapter uses an exact authorized snapshot plus
  the existing hash/BM25-style local scoring. HNSW ranking and Postgres full
  text retrieval are deferred to Phase 2, where the retrieval stages and
  ablations are defined.
- The synchronous `/v1/documents` route remains for a simple demo path; the
  asynchronous `/v1/ingestion/jobs` route and worker provide the Phase 1 job
  lifecycle.
- The current API retains the existing `version` request/response field as the
  compatibility name for `product_version`; database storage uses the explicit
  `product_version` column and exposes `revision` separately.
- The end-to-end document checks used public Markdown-like section payloads,
  not a large external corpus. Corpus acquisition and benchmark construction
  belong to Phase 3.
- The Compose image is pinned to the verified pgvector digest rather than only
  the mutable `pg17` tag.

## 6. Things I am unsure about

- The `pg17` image tag and the recorded digest are verified for this run; a
  future pgvector release may change the tag, so the digest should be changed
  only after a new official-doc and runtime verification.
- pgvector iterative-scan GUCs appear in `pg_settings` after `LOAD 'vector'` in
  a session. The test performs that explicit load; the application does not
  enable iterative scans yet because HNSW retrieval is Phase 2 work.
- Postgres retrieval currently loads authorized rows before local scoring rather
  than using an approximate vector index. This is inspectable and correct for
  the Phase 1 lifecycle tests, but it is not the large-corpus performance design.
- The running development Compose volume contains test fixtures from the
  integration runs. A clean-volume run should be used for a clean demo.

## 7. Abstractions or code that should be removed

- Reconsider the Pinecone adapter once the Postgres/pgvector path is the only
  production storage target; retain it only if a measured comparison requires
  it.
- Reconsider broad retrieval ports that still represent speculative future
  implementations; retain the shared contract where memory and Postgres are
  both real implementations.
- Keep `InMemoryVersionedStore`, `InMemoryHybridIndex`, the hash encoder,
  token-overlap reranker, and extractive generator as named test/baseline
  fixtures.
- The Phase 1 process-local cache in the original ingestion pipeline remains a
  local baseline; production Postgres ingestion should use the durable store.

Phase 1 is complete. The branch is pushed, and the next step is opening a PR
into `main`; it must not be merged until the project owner confirms.
