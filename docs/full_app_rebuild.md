# Full application corpus rebuild

## Purpose

Build the final application dataset from the complete three-version PostgreSQL
manual corpus, fill the missing BGE-small dense-vector coverage, and wire the
application to BGE-small retrieval plus the DeepSeek Flash answer generator.

This is an isolated application build. The source databases remain read-only and
are never used as mutation targets.

## Safety boundary

- Source databases: `evidence_rag_eval` and
  `evidence_rag_recovery_20261028`.
- Source connection policy: `default_transaction_read_only=on`.
- Target database: `evidence_rag_full_app_5d34bd5a2530`.
- Target status at start: did not exist.
- No source table, source schema, source volume, or existing volume may be
  deleted, truncated, migrated, or overwritten.
- Fine-tuned embedding models are excluded from this rebuild.

## Starting baseline

| Item | Count/value |
|---|---:|
| Documents | 1 |
| Document versions | 3 |
| Sections | 23,946 |
| Active chunks | 32,719 |
| BGE-small embedding records | 9,083 |
| BGE-small linked chunks | 20,756 |
| Active chunks without vector links | 11,963 |
| Vector dimensions | 384 |
| Embedder ID | `bge-small-en-v1.5` |

## Planned phases

1. Create the isolated target from the source without changing the source.
2. Verify target counts, schema, migrations, and source/target baseline hashes.
3. Inventory missing vector links and reusable content-hash vectors.
4. Reuse compatible vectors first; encode only genuinely missing unique texts with
   `BAAI/bge-small-en-v1.5` on CPU in resumable batches.
5. Validate dimensions, normalization, links, counts, and HNSW readiness.
6. Configure the final application for BGE-small retrieval and DeepSeek Flash.
7. Run full-corpus retrieval, ACL/version, API, and answer-verification checks.
8. Record final results, timings, resource use, and remaining limitations.

## Current status

- Preflight completed.
- Both source databases matched the baseline counts and embedder groups.
- Target `evidence_rag_full_app_5d34bd5a2530` created from the source template.
- Target counts and embedder groups match `evidence_rag_eval` exactly.
- No source or existing database was modified.
- Current migrations applied to the new target only.
- Inventory: 11,963 active chunks lack links, with 6,065 unique content hashes
  requiring encoding and zero reusable vectors among those missing links.
- Compatibility confirmed: `bge-small-en-v1.5`, 384 dimensions, normalized
  vectors, query instruction enabled, metadata prefix disabled.
- Timing batch: 64 texts encoded in 12.3s after a 6.0s model load; no writes.
- Batch 1: 1,024 vectors inserted, 1,981 links inserted, 187.7s encoding,
  5,041 unique hashes remaining.
- Batch 2: 1,024 vectors inserted, 2,058 links inserted, 194.8s encoding,
  4,017 unique hashes remaining.
- Batch 3: 1,024 vectors inserted, 1,995 links inserted, 197.2s encoding,
  2,993 unique hashes remaining.
- Batch 4: 1,024 vectors inserted, 2,015 links inserted, 211.4s encoding,
  1,969 unique hashes remaining.
- Batch 5: 1,024 vectors inserted, 2,024 links inserted, 208.6s encoding,
  945 unique hashes remaining.
- Final batch: 945 vectors inserted, 1,890 links inserted, 177.5s encoding,
  0 unique hashes remaining.
- Final target coverage: 32,719 active chunks, 32,719 valid BGE-small links,
  15,148 BGE-small vector records, all 384-dimensional.
- Protected verification after rebuild: 52 tables checked, 0 count mismatches,
  0 canonical SHA-256 mismatches.
- Full-corpus smoke passed with BGE-small CPU query encoding, PostgreSQL hybrid
  retrieval, `pg-17` filtering, 5 returned matches, citations, and no
  abstention. DeepSeek was intentionally not called during this smoke test.
- Final runtime wiring and live validation are recorded below.

## Final runtime verification — 2026-10-30

### Runtime configuration

- `.env` contains a non-empty `DEEPSEEK_API_KEY`; the value is never recorded
  here. A direct `deepseek-flash` streaming preflight returned HTTP 200 and a
  completed SSE stream before containers were started.
- Final database URL points to `evidence_rag_full_app_5d34bd5a2530` on the
  existing `evidence-rag-postgres-1` PostgreSQL 17.11 container through the
  existing `evidence-rag_default` network.
- Final models: `bge-small` / `BAAI/bge-small-en-v1.5`,
  `cross-encoder/ms-marco-MiniLM-L6-v2`, and `deepseek-flash`.
- BGE-small and the cross-encoder were loaded successfully on the host with
  offline mode. The host cache `/home/sharath/.cache/huggingface` is mounted
  read-only into `api` and `worker`; explicit `/hub` cache variables are set.
- Final API and UI ports are `18010` and `18511`. The API health endpoint
  reported 32,719 public manual chunks and the UI returned HTTP 200.
- The canonical `Dockerfile` build for `api`, `worker`, and `ui` succeeded after
  moving locked dependency installation before source copying and adding pip
  timeout/retry settings. The containers run canonical images; no patch image or
  scratch Dockerfile is used.
- Streamlit `AppTest` ran inside the canonical UI container against the live
  canonical API. An extractive hybrid query rendered the answer, `pg-17`
  version, citations, Claim support, Stage latency trace, and Persistent cost
  ledger with zero AppTest exceptions and zero UI errors.
- The demo was isolated in `.env.demo` and `docker-compose.demo.yml`; the
  running demo containers, port 15432, and `evidence_rag_demo_pgdata` volume
  remained untouched.

### ACL fixture and corpus boundary

- Added only to the final target: document
  `postgresql-sre-operations-policy`, version `fixture-v1`, 3 chunks, 3
  BGE-small 384-dimensional vectors, and private groups `sre`/`docs-admins`.
- The public manual corpus remained unchanged at 32,719 chunks, 23,946
  sections, three active public versions, and three public ACL rows. Target
  totals after the fixture are 2 documents, 4 versions, 23,949 sections,
  32,722 chunks, 15,151 vectors, 32,722 links, and 6 ACL rows.
- Pre/post manual fingerprints matched for documents, versions, sections,
  chunks, links, ACL rows, and referenced embedding rows.

### Acceptance matrix

The six legacy acceptance cases were re-run through the canonical API, with one
PG16 retry required to obtain a supported verified answer. The existing
unanswerable and exact-identifier verification cases remain in the ledger. The
ACL cases were local and did not call DeepSeek.

The case-level outputs, support flags, latencies, trace IDs, and post-fix token
cost samples are preserved in
`results/final_runtime_acceptance_20261030.md`.

| Case | Result | Evidence |
|---|---|---|
| PostgreSQL 15 version query | Passed | HTTP 200, `answered_version=pg-15`, 3 citations, supported claims, `$0.00059452` |
| PostgreSQL 16 version query | Passed | HTTP 200 after one retry, `answered_version=pg-16`, supported claim, `$0.00060218` |
| PostgreSQL 17 version query | Passed | HTTP 200, `answered_version=pg-17`, 3 supported citations, `$0.00058102` |
| Exact `max_wal_senders` query | Passed | HTTP 200, supported claims and citations, `$0.00053888` |
| Quote/claim verification | Passed | Verbatim quotes, citation checks, supported claims, `$0.00064942` |
| Public answer | Passed | HTTP 200, 2 supported claims, 2 citations, `$0.00049728` |
| Unanswerable question | Passed | DeepSeek returned `not found`; local verification abstained with 0 citations |
| ACL allow (`bob`, `sre`) | Passed locally | 3 private chunks retrieved with extractive generation; no provider call |
| ACL deny (`alice`, public-only) | Passed locally | `not found`, 0 matches, 0 citations, no provider call |

All listed DeepSeek traces now persist non-empty token usage, provider latency,
attempt count, and positive `cost_usd`. The complete token and cost ledger is
in `results/final_runtime_acceptance_20261030.md`; account billing is not
observable. The two PG16 retry traces also have complete metadata, with the
successful trace used in the acceptance table.

### Safety and build notes

- The existing PostgreSQL container and volume were never stopped, recreated,
  removed, or overwritten. No `down -v` or `--remove-orphans` command was run.
- The canonical Docker image build succeeded from `Dockerfile` with resilient
  pip settings. Obsolete local `:patched` image tags were removed after the
  canonical containers started. No database or protected volume was involved.
- No commit, merge, or push has been performed for this runtime work.

## Decision rule

If existing BGE-small vector configuration cannot be proven compatible with the
newly encoded vectors, the rebuild will use a separate embedder ID and re-embed
all unique corpus hashes rather than mixing incompatible vectors.
