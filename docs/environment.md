# Environment and provider record

Last reviewed: 2026-10-28 (Phase 6 provider selection and official API documentation).

## Answers from the project owner

| Question | Recorded answer | Source |
| --- | --- | --- |
| LLM provider | DeepSeek OpenAI-compatible endpoint only: `https://api.deepseek.com/chat/completions` | Owner's Phase 6 implementation instruction; supersedes Phase 0's provisional Gemini selection |
| Fixed model | `deepseek-flash`; no Velona, Gemini, or V4 Pro calls | Owner's Phase 6 instruction |
| Key availability | `DEEPSEEK_API_KEY` in ignored `.env`, with process environment taking precedence. No key is committed. | Local presence check; values never logged |
| Budget | Historical target was $0 paid spend. Owner explicitly requested this cached DeepSeek run; estimated token costs are recorded, but actual billing/granted balance is not observable. No free-tier claim is made. | Phase 0 target and Phase 6 execution instruction |
| Embeddings/reranker | Local models only; no paid embedding API | Owner answer in Phase 0 session |
| Runtime OS | Ubuntu under WSL2; use `python3` and the repository `.venv` | Owner answer in Phase 0 session |
| Training environment | Google Colab free GPU for Phase 5 | Owner answer in Phase 0 session |
| Data policy | Only public documents may be sent to an external API | Owner answer in Phase 0 session |

## Phase 6 provider verification

Official DeepSeek documentation inspected on 2026-10-28:

- <https://api-docs.deepseek.com/guides/thinking_mode>: Chat Completions uses
  `thinking: {type: disabled}` to disable default-on reasoning. `reasoning_effort`
  alone controls effort and is not used as a substitute for the thinking toggle.
- <https://api-docs.deepseek.com/quick_start/pricing>: `deepseek-flash` currently
  maps to DeepSeek-V4.1-Flash-1017. Per million tokens, off-peak/peak USD rates are
  $0.003/$0.006 input cache-hit, $0.15/$0.30 input cache-miss, $0.60/$1.20 output.
  Reports record this cost range from returned usage, not fabricated billed dollars.
- Requests use `temperature=0`, `stream=true`, JSON output and streamed usage.
  Each attempt has a strict 45-second wall-clock deadline as well as HTTP timeouts.
  Requests are throttled by 0.5s and HTTP 429/5xx retry with exponential backoff,
  at most three attempts. Authentication/schema/truncation failures are not retried.
- Phase 6 evaluation completions live only in `.cache/phase6/`, keyed by model,
  full prompt/request hash, question ID and context hash. Entries retain usage,
  latency, attempts and estimated cost. Errors and incomplete streams are not cached.
- Serving selects the provider with `RAG_GENERATION_BACKEND=deepseek-flash` and
  reads the dev threshold from `configs/phase6_calibration.json`. Extractive is
  the default. Serving never constructs/imports the evaluation cache.
- PostgreSQL serving rechecks current public ACLs before external generation.
  Private or unauthorized chunks, unresolved scope and empty authorized contexts
  never reach the provider. The evaluation uses a public manual snapshot and
  the simulated `data/acl_demo.yaml` policy; denied restricted-collection requests
  abstain locally. Evidence is checked again against the exact transmitted text.

See `results/phase6_results.json` and `docs/phase6_findings.md` for the completed
run's measurements, human-reference alignment and limitations.

### Historical Phase 0 provisional provider (superseded)

The intended Gemini OpenAI-compatible base URL is recorded as:

```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

The intended request shape is the OpenAI chat-completions shape already used by
the adapter, with `temperature=0`. The official Google AI documentation URL is
<https://ai.google.dev/gemini-api/docs/openai>. Attempts to fetch that page on
2026-10-02 returned HTTP 429 from this environment. Therefore the endpoint,
free-tier status, limits, and the provisional model above are **not yet verified
for this run**. Revalidate from the official Google documentation and the
provider's model-list endpoint after the owner creates a key, before any Phase 6
experiment. Do not treat the provisional name as a measured or guaranteed
availability claim.

The official Google-maintained Gen AI SDK documentation was reachable at
<https://raw.githubusercontent.com/googleapis/python-genai/main/README.md> and
demonstrates current model aliases such as `gemini-flash-latest`; it is not used
as proof of AI Studio free-tier limits or a fixed model choice. Model license,
price, rate limits, and context/output limits remain an explicit Phase 6
verification item.

## Operational constraints

- Keep `DEEPSEEK_API_KEY` and all other credentials out of source control and logs.
- API calls are not made in CI.
- Later evaluation-only LLM/API-embedding calls must be cached under `.cache/`
  by model and prompt hash; errors are never cached and cost is recorded.
- Request throttling, exponential backoff and total HTTP deadlines are implemented
  in the Phase 6 provider adapter.
- The serving API must not use the evaluation cache.

## Local toolchain

The environment initially lacked `python3-venv` and pip. A no-`ensurepip`
virtual environment was created and pip was bootstrapped from
<https://bootstrap.pypa.io/get-pip.py>. The exact installed versions are
recorded by `docs/status.md` and the pinned lock file.

## Phase 1 pgvector verification

The repository initially had no pgvector image installed. On 2026-10-03, the
official `pgvector/pgvector:pg17` image was pulled and queried directly. The
image digest was:

```text
sha256:ac08538c6f8b9904c33c8224c5e5706dbe760aca29db1d096972b4052c22a75d
```

The actual database output was:

```text
postgres_version: 17.11 (Debian 17.11-1.pgdg12+2)
extversion: 0.8.7
hnsw.iterative_scan: off
ivfflat.iterative_scan: off
hnsw.max_scan_tuples: 20000
hnsw.scan_mem_multiplier: 1
ivfflat.max_probes: 32768
```

The command also created an HNSW index on `vector(2000)` successfully. The
official pgvector README at
<https://raw.githubusercontent.com/pgvector/pgvector/master/README.md> was
reachable and identifies the source/Docker release as `v0.8.7`. It documents
HNSW and IVFFlat, iterative scans beginning in 0.8.0, and these index limits:

| Type | Indexed limit documented by pgvector |
| --- | ---: |
| `vector` | 2,000 dimensions for HNSW/IVFFlat |
| `halfvec` | 4,000 dimensions for HNSW/IVFFlat |
| `bit` | 64,000 dimensions |
| `sparsevec` | 1,000 non-zero elements for HNSW |

The same documentation says the storage type can hold up to 16,000 dimensions
for `vector` and `halfvec`, which is distinct from the approximate-index limit.
The implementation therefore records the embedder dimension explicitly and will
reject an index configuration above the verified HNSW limit rather than silently
assuming support.

Sources consulted:

- <https://raw.githubusercontent.com/pgvector/pgvector/master/README.md>
- <https://github.com/pgvector/pgvector/releases>
- <https://www.postgresql.org/docs/current/gin.html>

## Phase 2 retrieval verification

- The rebuilt local environment is Python 3.12.15 with `torch==2.14.1+cpu` and
  `sentence-transformers==6.1.0`; BGE-small produced 384-dimensional normalized
  embeddings and `cross-encoder/ms-marco-MiniLM-L6-v2` produced a reranking score.
- BGE small and base model cards identify the released models as MIT licensed:
  <https://huggingface.co/BAAI/bge-small-en-v1.5> and
  <https://huggingface.co/BAAI/bge-base-en-v1.5>.
- The configurable cross-encoder is Apache-2.0 licensed:
  <https://huggingface.co/cross-encoder/ms-marco-MiniLM-L6-v2>.
- The exact pgvector 0.8.7 README checked for HNSW, GIN/full-text hybrid search,
  and iterative scans is <https://raw.githubusercontent.com/pgvector/pgvector/v0.8.7/README.md>.
- Phase 2 uses the verified 384-dimension HNSW expression index, an identifier
  GIN index, `hnsw.iterative_scan=strict_order`, and retains exact fallback search.
