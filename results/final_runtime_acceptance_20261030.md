# Final runtime acceptance — 2026-10-30

## Environment

- API: `http://127.0.0.1:18010`
- UI: `http://127.0.0.1:18511`
- Database: `evidence_rag_full_app_5d34bd5a2530` on PostgreSQL 17.11
- Dense model: `BAAI/bge-small-en-v1.5`, CPU, 384 dimensions
- Reranker: `cross-encoder/ms-marco-MiniLM-L6-v2`, CPU
- Generator: `deepseek-flash`
- Trace lookup: every listed trace returned HTTP 200 from `/v1/traces/{id}`
- Secret values and full provider payloads are intentionally excluded.

## Application cases

| Case | HTTP | Latency (s) | Answer/result | Citations | Claim support | Trace |
|---|---:|---:|---|---:|---|---|
| PG 15 version | 200 | 12.834 | `max_wal_senders` specifies the maximum concurrent connections from standby servers or streaming base-backup clients | 3 | `[true, true, true]` | `631e6f76-c9c0-4b64-a5af-edca33a32679` |
| PG 16 version | 200 | 5.883 | Semaphore sizing answer; supported claim retained after one retry | 1 | `[true]` | `ef75e7b3-0b8f-4541-8e8d-b37682495d1f` |
| PG 17 version | 200 | 6.015 | Concurrent standby/streaming-backup connections, WAL sender processes, default 10 | 3 | `[true, true, true]` | `bab9eb41-d095-4e01-b9cc-a5fe5c1c2c22` |
| Exact identifier | 200 | 5.725 | `max_wal_senders` purpose, default 10, and value 0 disables replication | 3 | `[true, true, true]` | `e449f401-e03c-4d83-b928-39292ca60d3a` |
| Quote/claim verification | 200 | 6.857 | Kernel-resource and semaphore relationship explanation | 2 | `[true, true]` | `212b90f1-fc0f-43a0-bfac-221165f27284` |
| Public answer | 200 | 5.647 | Managing-kernel-resources guidance explanation | 2 | `[true, true]` | `74636f7f-e8d6-4bda-b5fd-538bd9294ac7` |
| Unanswerable query | 200 | 6.861 | `not found` | 0 | abstained | `8a50f835-7ebe-47d4-a31a-35a4b6dfe903` |
| Exact identifier, post-fix repeat | 200 | 5.002 | `max_wal_senders` purpose, default 10, and value 0 disables replication | 3 | `[true, true, true]` | `6a59bea7-5499-479a-812b-27418507ab8e` |

The first six rows plus the unanswerable row and post-fix repeat equal eight
live application DeepSeek calls. The separate preflight was one connectivity
call with a 16-token limit and was not part of the acceptance count.

## ACL cases

| Case | HTTP | Latency (s) | Result | Matches | Citations | Provider call | Trace |
|---|---:|---:|---|---:|---:|---|---|
| `bob`, group `sre` | 200 | 0.315 | Local extractive answer from the private fixture | 3 | 1 | No | `13dfd003-5055-43e5-8664-2470e2cd85e1` |
| `alice`, public-only | 200 | 0.064 | `not found`; local abstention | 0 | 0 | No | `56949b71-2336-422a-9b80-4f0bf061ab2d` |

The denial trace has resolved scope with no authorized versions and no provider
metadata. No private passage was sent to DeepSeek.

## Complete provider accounting

All listed provider traces persist `model`, token `usage`, provider latency,
attempt count, and a public peak-rate estimate. Account billing is not observable.

| Case | Prompt tokens | Cache hit | Cache miss | Completion tokens | Total tokens | Cost USD | Trace |
|---|---:|---:|---:|---:|---:|---:|---:|
| PG 15 | 1,747 | 1,536 | 211 | 435 | 2,182 | `$0.00059452` | `631e6f76-c9c0-4b64-a5af-edca33a32679` |
| PG 16 | 1,858 | 1,664 | 194 | 445 | 2,303 | `$0.00060218` | `ef75e7b3-0b8f-4541-8e8d-b37682495d1f` |
| PG 17 | 1,758 | 1,536 | 222 | 421 | 2,179 | `$0.00058102` | `bab9eb41-d095-4e01-b9cc-a5fe5c1c2c22` |
| Exact identifier | 1,799 | 1,664 | 135 | 407 | 2,206 | `$0.00053888` | `e449f401-e03c-4d83-b928-39292ca60d3a` |
| Quote/claim | 1,726 | 1,536 | 190 | 486 | 2,212 | `$0.00064942` | `212b90f1-fc0f-43a0-bfac-221165f27284` |
| Public answer | 1,476 | 1,280 | 196 | 359 | 1,835 | `$0.00049728` | `74636f7f-e8d6-4bda-b5fd-538bd9294ac7` |
| Unanswerable | 1,948 | 0 | 1,948 | 15 | 1,963 | `$0.00060240` | `8a50f835-7ebe-47d4-a31a-35a4b6dfe903` |
| Exact identifier repeat | 1,807 | 1,152 | 655 | 450 | 2,257 | `$0.00074341` | `6a59bea7-5499-479a-812b-27418507ab8e` |

All eight acceptance cases now have non-empty persisted token usage, provider
latency, attempt count, and positive `cost_usd`. The two PG16 retry attempts
also have complete metadata; the accepted PG16 trace above is the successful
verification row.

## Canonical UI verification

`streamlit.testing.v1.AppTest` ran inside the canonical `evidence-rag-final-ui-1`
container against the live `api:8000` service. One extractive hybrid query
rendered an answer, `version=pg-17`, citations, Claim support, Stage latency
trace, and Persistent cost ledger. AppTest exception count and error count were
both zero. The canonical Docker images were built from `Dockerfile`; obsolete
`:patched` image tags were removed.
