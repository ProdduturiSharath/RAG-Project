# Phase 6 results

Frozen 60-question test set; mean [bootstrap 95% CI].

| Arm | Correctness* | Faithfulness* | Citation precision* | Abstention correctness | Wrong-version answers | Answered |
| --- | --- | --- | --- | --- | --- | ---: |
| extractive | 0.283 [0.188, 0.424] | 0.243 [0.185, 0.314] | 1.000 [1.000, 1.000] | 0.800 [0.646, 1.000] | 0.000 [0.000, 0.000] | 57 |
| extractive-verified | 0.317 [0.100, 0.493] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.667 [0.542, 0.771] | 0.000 [0.000, 0.000] | 25 |
| llm-unverified | 0.617 [0.436, 0.754] | 0.876 [0.743, 0.970] | 1.000 [1.000, 1.000] | 0.900 [0.769, 1.000] | 0.000 [0.000, 0.000] | 39 |
| llm-verified | 0.517 [0.278, 0.673] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 0.767 [0.522, 0.912] | 0.000 [0.000, 0.000] | 31 |

*Deterministic lexical-reference / quote-support proxies, not human semantic judgments. Faithfulness and citation precision exclude abstentions.
Wrong-version rate uses all 60 questions as denominator. CIs resample lineage clusters (2,000 draws, seed 42).
