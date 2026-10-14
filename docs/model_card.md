# Phase 5 model card

## Purpose

Phase 5 tests whether open dense retrievers fine-tuned on PostgreSQL documentation
queries beat the Phase 4 bge-small dense arm, BM25, and the Phase 4 recommended
hybrid arm on `data/eval/gold.jsonl`.  The corpus is PostgreSQL 15, 16, and 17
documentation materialized from the persisted section-family split.  Training
passages are unique by content hash, restricted to `text` and `table` records,
200–1,800 characters, and exclude reference-only stubs.

## Generator market review (checked 2026-10-14)

`scripts/phase5_prepare.py` discovers the live model catalogs rather than using a
fixed model allow-list.  It records the catalog response, model IDs, provider
documentation, terms URL, rate-limit URL, and the independent quality sources in
`data/train/generator_market.json`.  The market sweep queries NVIDIA, Google,
Groq, Cerebras, Mistral, Together, Fireworks, DeepSeek, Cohere, Hugging Face,
GitHub Models, OpenAI, Anthropic, and xAI when their keys are present.  Native
protocols are audited but cannot silently enter the OpenAI-compatible trial.

Independent quality evidence used for ranking is the Artificial Analysis model
leaderboard ([models](https://artificialanalysis.ai/leaderboards/models)) and the
LMArena text leaderboard ([text](https://lmarena.ai/leaderboard/text)), both
checked 2026-10-14.  These sources are ranking signals only; they do not replace
the local ten-passage trial.

The initial shortlist to verify at runtime is:

| Provider/model | Key | Terms/rate-limit decision |
| --- | --- | --- |
| NVIDIA `nvidia/llama-3.3-nemotron-super-49b-v1.5` | existing `NVIDIA_API_KEY` | NVIDIA's [LLM API catalog](https://docs.api.nvidia.com/nim/reference/llm-apis) exposes a stable ID and API, but the linked public agreement did not clearly grant output-training rights; flagged until confirmed. |
| Groq `openai/gpt-oss-120b` | `GROQ_API_KEY` | [Models](https://console.groq.com/docs/models) and [limits](https://console.groq.com/docs/rate-limits) are documented, but the free plan's 1,000 RPD is below the roughly 1,500-call budget; excluded for this run. |
| OpenAI API stable model returned by `/v1/models` | `OPENAI_API_KEY` | [Services Agreement §3.3(e), §4.1, and “Permitted Exception”](https://openai.com/policies/services-agreement/) permit non-distributed categorization/organization models and assign output ownership, but this is paid and therefore requires explicit approval. |

The script excludes anonymous, stealth, alpha, beta, preview, experimental, and
deprecated IDs; candidates with unclear terms or no documented way to disable
thinking are flagged/excluded.  If no free candidate clears all gates, the
script reports the cheapest permitted paid candidate and exits before making a
paid call.  No API call or `.env` read was made while implementing this branch.

For each candidate, the host must pass: valid JSON for at least 9/10 trial
passages, no truncation, at least 80% distinct query openings, and median latency
under 30 seconds.  Generation uses three passages per request, temperature 0.8,
backoff, provider throttling, and a cache under `.cache/phase5`.

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

The GPU stage reads the current public [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
and Hugging Face sentence-similarity catalog, checked 2026-10-14, then keeps up
to five English, permissively licensed models with no more than 600M parameters
and 1,024 dimensions.  It always includes:

* `BAAI/bge-base-en-v1.5` and `BAAI/bge-large-en-v1.5`: query prefix
  `Represent this sentence for searching relevant passages: `; no passage prefix.
* `intfloat/e5-base-v2` and `intfloat/e5-large-v2`: `query: ` and `passage: `.
* `sentence-transformers/all-MiniLM-L12-v2`: no prefix when it is retained as
  the fifth candidate.

Model cards and the exact selected catalog entries are saved in
`phase5_outputs/run_summary.json`; no prefix is inferred silently.

## Fine-tuning setup

`BAAI/bge-small-en-v1.5` and `BAAI/bge-base-en-v1.5` are fine-tuned separately
with seeds 1, 2, and 3 using `MultipleNegativesRankingLoss` on
`(query, positive, hard-negative)` examples.  The query prefix is applied to
queries only.  Training is fixed at fp16, learning rate `2e-5`, 10% warmup, two
epochs, batch size 16, and no hyperparameter search.  Checkpoints, corpus
vectors, evaluation-query vectors, hard negatives, dependency/runtime versions,
and checkpoint hashes are packaged in `phase5_outputs.tar.gz`.

## Evaluation and limits

The host imports vectors into an isolated Postgres schema and evaluates dense,
BM25, weighted hybrids, fine-tuned seed aggregates, type/paraphrase cohorts,
confusion@1, and paired lineage bootstrap comparisons.  Alpha is selected on
DEV only from `{0.25, 0.5, 0.75}`.  A three-question smoke gate and Phase 4
zero-score guard run before the long evaluation.  SciFact nDCG@10 is compared
with its published `0.71275` figure as a forgetting check when the selected model
and network are available.

Questions are model-written on both sides and can favor lexical overlap; BM25
may remain ahead.  The evaluation corpus includes training passages, cohorts are
small, and no result is a claim about unseen documentation or answer quality.
The Phase 4 recommended replay is documented separately in generated findings
when the host evaluation completes; this branch does not invent a metric before
that run.
