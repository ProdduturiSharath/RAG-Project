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
| alice | — | 0.526/1.038 | 0.539/1.263 | 0 | 0 |
| bob | sre | 0.436/0.570 | 0.548/0.845 | 0 | 0 |
| mallory | — | 0.393/0.524 | 0.472/0.619 | 0 | 0 |

## Filtered ANN recall

| Mode | Recall@10 | p50 ms | p95 ms |
| --- | ---: | ---: | ---: |
| off | 1.000 | 14.850 | 16.894 |
| strict_order | 1.000 | 13.933 | 14.807 |
| exact ground truth | 1.000 | 15.412 | 17.294 |

HNSW index `phase7_ann_scope_hnsw` used: **True**; selective scope rows: 382 of 20634.
