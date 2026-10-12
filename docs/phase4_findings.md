# Phase 4 findings

Generated from the current `results/*.json` artifacts; no metrics are hand-copied.

## Test headline

Values are means [lineage-bootstrap 95% CI].

| System | R@1 | R@5 | MRR | nDCG@10 | Confusion@1 |
| --- | --- | --- | --- | --- | --- |
| default | 0.244 [0.120, 0.369] | 0.402 [0.240, 0.577] | 0.333 [0.207, 0.460] | 0.379 [0.260, 0.497] | 0.238 [0.125, 0.556] |
| bm25 | 0.341 [0.211, 0.481] | 0.701 [0.590, 0.812] | 0.486 [0.373, 0.595] | 0.553 [0.446, 0.646] | 0.190 [0.043, 0.750] |
| hybrid-bm25-weighted-025 | 0.366 [0.189, 0.530] | 0.677 [0.525, 0.817] | 0.504 [0.339, 0.649] | 0.563 [0.417, 0.691] | 0.143 [0.030, 0.429] |
| scope-explicit | 0.402 [0.247, 0.592] | 0.604 [0.428, 0.768] | 0.498 [0.348, 0.671] | 0.539 [0.390, 0.696] | 0.000 [0.000, 0.000] |
| parent-off | 0.244 [0.120, 0.369] | 0.561 [0.423, 0.688] | 0.380 [0.255, 0.504] | 0.431 [0.306, 0.545] | 0.238 [0.125, 0.556] |
| recommended | 0.439 [0.274, 0.598] | 0.738 [0.627, 0.839] | 0.558 [0.423, 0.689] | 0.612 [0.498, 0.719] | 0.000 [0.000, 0.000] |

## Findings

### Recommended versus default
dev: paired nDCG@10 Δ (recommended − default) is +0.195 [+0.090, +0.295], CI excludes zero test: paired nDCG@10 Δ (recommended − default) is +0.232 [+0.140, +0.322], CI excludes zero.

### Recommended versus BM25
dev: paired nDCG@10 Δ (recommended − bm25) is +0.049 [-0.005, +0.109], within noise test: paired nDCG@10 Δ (recommended − bm25) is +0.059 [-0.036, +0.130], within noise.

### Cross-encoder variant versus recommended
dev: paired nDCG@10 Δ (recommended-cross-encoder − recommended) is -0.048 [-0.135, +0.045], within noise test: paired nDCG@10 Δ (recommended-cross-encoder − recommended) is -0.068 [-0.155, +0.030], within noise dev total-latency Δ is +1482.6 ms test total-latency Δ is +1962.2 ms.

### Dense plus BM25 hybrid versus default
dev: paired nDCG@10 Δ (hybrid-bm25-weighted-025 − default) is +0.128 [+0.045, +0.200], CI excludes zero test: paired nDCG@10 Δ (hybrid-bm25-weighted-025 − default) is +0.184 [+0.096, +0.284], CI excludes zero.

### Explicit version scope versus default
dev: paired nDCG@10 Δ (scope-explicit − default) is +0.171 [+0.112, +0.238], CI excludes zero test: paired nDCG@10 Δ (scope-explicit − default) is +0.160 [+0.099, +0.250], CI excludes zero.

### Parent expansion ablation versus default
dev: paired nDCG@10 Δ (parent-off − default) is +0.048 [+0.036, +0.061], CI excludes zero test: paired nDCG@10 Δ (parent-off − default) is +0.051 [+0.033, +0.067], CI excludes zero.

## Paraphrase breakdown

`paraphrased=true` is the cohort used to show performance when the parameter name is absent.

| System | Split | Paraphrased | Scored n | R@1 | R@5 | MRR | nDCG@10 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bm25 | dev | false | 61 | 0.451 [0.308, 0.563] | 0.730 [0.615, 0.824] | 0.592 [0.473, 0.695] | 0.630 [0.522, 0.721] |
| bm25 | dev | true | 33 | 0.561 [0.389, 0.655] | 0.682 [0.500, 0.806] | 0.665 [0.491, 0.770] | 0.675 [0.513, 0.767] |
| bm25 | test | false | 62 | 0.306 [0.163, 0.511] | 0.653 [0.533, 0.778] | 0.451 [0.318, 0.615] | 0.516 [0.389, 0.658] |
| bm25 | test | true | 20 | 0.450 [0.222, 0.632] | 0.850 [0.750, 1.000] | 0.596 [0.478, 0.735] | 0.667 [0.600, 0.789] |
| dense-bge-small | dev | false | 61 | 0.148 [0.036, 0.275] | 0.344 [0.173, 0.531] | 0.233 [0.110, 0.363] | 0.278 [0.140, 0.420] |
| dense-bge-small | dev | true | 33 | 0.318 [0.160, 0.415] | 0.561 [0.370, 0.694] | 0.432 [0.281, 0.531] | 0.463 [0.326, 0.560] |
| dense-bge-small | test | false | 62 | 0.210 [0.074, 0.360] | 0.435 [0.262, 0.651] | 0.314 [0.160, 0.484] | 0.346 [0.189, 0.522] |
| dense-bge-small | test | true | 20 | 0.250 [0.050, 0.529] | 0.350 [0.125, 0.600] | 0.318 [0.094, 0.569] | 0.349 [0.113, 0.575] |
| hybrid-bm25-weighted-025 | dev | false | 61 | 0.402 [0.300, 0.509] | 0.697 [0.569, 0.801] | 0.550 [0.455, 0.640] | 0.606 [0.509, 0.691] |
| hybrid-bm25-weighted-025 | dev | true | 33 | 0.530 [0.289, 0.642] | 0.742 [0.519, 0.863] | 0.658 [0.444, 0.766] | 0.669 [0.478, 0.762] |
| hybrid-bm25-weighted-025 | test | false | 62 | 0.339 [0.179, 0.510] | 0.685 [0.544, 0.845] | 0.488 [0.329, 0.653] | 0.541 [0.396, 0.692] |
| hybrid-bm25-weighted-025 | test | true | 20 | 0.450 [0.143, 0.647] | 0.650 [0.333, 0.857] | 0.556 [0.330, 0.706] | 0.632 [0.453, 0.751] |

## Recommended by question type (test)

| Type | Scored n | R@1 | R@5 | MRR | nDCG@10 | Confusion@1 |
| --- | --- | --- | --- | --- | --- | --- |
| acl | 1 | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | 1.000 [1.000, 1.000] | — |
| exact_identifier | 16 | 0.375 [0.214, 0.538] | 0.688 [0.421, 1.000] | 0.493 [0.372, 0.656] | 0.561 [0.411, 0.722] | — |
| factoid | 18 | 0.556 [0.200, 0.789] | 0.889 [0.840, 1.000] | 0.657 [0.440, 0.814] | 0.727 [0.577, 0.835] | — |
| multi_hop | 2 | 0.500 [0.500, 0.500] | 0.750 [0.750, 0.750] | 1.000 [1.000, 1.000] | 0.745 [0.745, 0.745] | — |
| table | 7 | 0.429 [0.125, 0.833] | 0.429 [0.125, 0.833] | 0.459 [0.170, 0.842] | 0.470 [0.197, 0.833] | — |
| unanswerable | 0 | — | — | — | — | — |
| unchanged_control | 17 | 0.235 [0.000, 0.600] | 0.529 [0.250, 0.800] | 0.360 [0.127, 0.708] | 0.421 [0.191, 0.726] | — |
| version_specific | 21 | 0.524 [0.238, 0.875] | 0.905 [0.733, 1.000] | 0.652 [0.423, 0.899] | 0.722 [0.530, 0.915] | 0.000 [0.000, 0.000] |
| version_unavailable | 0 | — | — | — | — | — |

## Failure categories

Reports used: recommended, recommended-cross-encoder, scope-explicit.

Counts are listed failure examples in the current failure reports.

| Category | Count | Three examples |
| --- | ---: | --- |
| identifier not matched | 3 | `recommended-cross-encoder/draft-e5b5f0b94a5943be`, `scope-explicit/draft-e5b5f0b94a5943be`, `scope-explicit/draft-32068527036ef646` |
| other | 81 | `recommended-cross-encoder/draft-33d8c19a2a6a932d`, `recommended-cross-encoder/draft-a2cf6aa49912f6e7`, `recommended-cross-encoder/draft-d1b8f6b5aa7eddfa` |
| text gap | 6 | `recommended-cross-encoder/draft-9b1f37bc7842b40e`, `recommended-cross-encoder/draft-dadefc52fd565605`, `recommended/draft-9b1f37bc7842b40e` |

## Limits

- Questions are model-written from passages and therefore favor lexical overlap.
- Explicit-scope version confusion is zero by construction.
- Only 101 of 212 questions name a version.
- Cohorts are small, so several confidence intervals are wide.
- Some arm rankings flip between DEV and TEST; only differences whose CI excludes zero count.
- The sparse diagnostic's `gold_ranks` contradicted its own top-3 and is not relied on.
- PostgreSQL full-text ranking is much weaker than BM25.
