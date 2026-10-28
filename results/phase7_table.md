# Phase 7 security and study results

All external API calls: **0**.

## Prompt-injection benchmark

| Adapter | Cases | Attack success before | Attack success after | Claim survival before | Claim survival after | Citation spoof before | Citation spoof after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| extractive | 6 | 0.000 | 0.000 | 0.000 | 0.000 | 0.333 | 0.000 |
| deterministic-llm | 6 | 1.000 | 0.000 | 1.000 | 0.000 | 0.667 | 0.000 |

## PostgreSQL RLS

| Principal | Groups | RLS p50/p95 ms | App SQL p50/p95 ms | RLS leakage count | App leakage count |
| --- | --- | ---: | ---: | --- | --- |
| alice | — | 0.218/0.613 | 0.326/0.544 | 0 | 0 |
| bob | sre | 0.216/0.415 | 0.293/0.366 | 0 | 0 |
| mallory | — | 0.292/0.477 | 0.358/0.562 | 0 | 0 |

## Filtered ANN recall

| Mode | Recall@10 | p50 ms | p95 ms |
| --- | ---: | ---: | ---: |
| off | 1.000 | 7.134 | 8.883 |
| strict_order | 1.000 | 7.024 | 7.700 |
| exact ground truth | 1.000 | 6.914 | 8.665 |

HNSW index `phase7_ann_scope_hnsw` used: **True**; selective scope rows: 383 of 20756.
