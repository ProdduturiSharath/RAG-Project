# Phase 5 model card

## Purpose

Phase 5 tests whether open dense retrievers fine-tuned on PostgreSQL documentation
queries beat the Phase 4 bge-small dense arm, BM25, and the Phase 4 recommended
hybrid arm on `data/eval/gold.jsonl`.  The corpus is PostgreSQL 15, 16, and 17
documentation materialized from the persisted section-family split.  Training
passages are unique by content hash, restricted to `text` and `table` records,
200–1,800 characters, and exclude reference-only stubs.

## Generator market review (checked 2026-10-14)

`scripts/phase5_prepare.py` uses the locked, static Lineup A; it does not scrape
provider catalogs.  Configured keys enable DeepSeek V4 Pro/Flash and Velona Qwen
3.7 Plus, with Velona fallback IDs registered when only the Velona key exists.
The exact endpoint, terms status, free status, and model metadata are recorded in
`data/train/generator_market.json` without recording secret values.

| Provider/model | Key | Terms/rate-limit decision |
| --- | --- | --- |
| DeepSeek `deepseek-v4-pro`, `deepseek-flash` | `DEEPSEEK_API_KEY` | MIT; permitted for this use; permitted free status. |
| Velona `qwen/qwen3.7-plus` | `VELONA_API_KEY` | Permitted for this use; permitted free status. |

The host trial sends standard OpenAI-compatible `messages`, temperature `0.8`,
`max_tokens=4096`, and standard `json_object` mode.  It deliberately omits
reasoning controls and strict JSON schemas because the approved endpoints reject
those fields.  `--sample N` prints grouped model/passage/style output without
starting the full batch.

The trial records validity, truncation, opening diversity, latency, and failure
diagnostics, but does not silently remove a configured/keyed model from the
active lineup.  All active models are round-robin scheduled; a failed
three-passage request is retried one passage at a time, and an unrecoverable
model failure stops the run instead of falling back to another wallet.
Generation uses three passages per request, visible batch progress, and a cache
under `.cache/phase5`.

## Training data and filtering

Each accepted passage receives four query styles: exact identifier/parameter,
behavior without the identifier, practitioner troubleshooting, and short
keyword search.  Unanswerable outputs, behavior queries naming the source
identifier, near duplicates, exclusion matches, and queries whose source is not
in the top 200 of either BM25 or off-the-shelf bge-small are dropped.  The
exclusion set contains normalized gold evidence quotes plus all gold and
candidate questions, including rejected draft questions.

Hard negatives are mined only among TRAIN passages using BM25 and off-the-shelf
bge-small ranks 3–30.  A negative is rejected when its normalized text,
content hash, or section family matches the positive.  This is deliberately
stricter than a text-only check because equivalent PostgreSQL versions can be
false negatives.

## Embedding sweep

The GPU stage uses a static, verified five-model 2026 MTEB lineup (no live
Hugging Face scraping):

* `BAAI/bge-base-en-v1.5` and `BAAI/bge-large-en-v1.5`: query prefix
  `Represent this sentence for searching relevant passages: `; no passage prefix.
* `Qwen/Qwen3-Embedding-0.6B`: the web-search instruction prefix.
* `Snowflake/snowflake-arctic-embed-l-v2.0`: `query: `.
* `BAAI/bge-m3`: no prefix.

Model cards and the exact selected catalog entries are saved in
`phase5_outputs/run_summary.json`; no prefix is inferred silently.

## Fine-tuning setup

`BAAI/bge-small-en-v1.5` and `BAAI/bge-base-en-v1.5` are fine-tuned separately
with seeds 1, 2, and 3; `Snowflake/snowflake-arctic-embed-m-v1.5` uses seed 1.
All use `MultipleNegativesRankingLoss` on
`(query, positive, hard-negative)` examples.  The query prefix is applied to
queries only.  Training is fixed at fp16, learning rate `2e-5`, 10% warmup, two
epochs, batch size 16, and no hyperparameter search.  Checkpoints, corpus
vectors, evaluation-query vectors, hard negatives, dependency/runtime versions,
and checkpoint hashes are packaged in `phase5_outputs.tar.gz`.

## Evaluation and limits

The host imports vectors into an isolated Postgres schema and evaluates dense,
BM25, weighted hybrids, fine-tuned per-question seed means, and paired lineage
bootstrap comparisons.  Phase 4 recommended uses alpha `0.25`; fine-tuned
recommended alpha is selected on DEV.  Strict quote metrics remain unchanged;
the reports also include windowed recall@5 and section-family recall@5.  The GPU
run stores SciFact scores for the baseline, sweep, and fine-tuned models so the
host does not re-encode the SciFact corpus.

Questions are model-written on both sides and can favor lexical overlap; BM25
may remain ahead.  The evaluation corpus includes training passages, cohorts are
small, and no result is a claim about unseen documentation or answer quality.
The Phase 4 recommended replay is documented separately in generated findings
when the host evaluation completes; this branch does not invent a metric before
that run.
