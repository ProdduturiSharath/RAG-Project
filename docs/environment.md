# Environment and provider record

Last reviewed: 2026-10-02 (UTC, from the session environment).

## Answers from the project owner

| Question | Recorded answer | Source |
| --- | --- | --- |
| LLM provider | Google Gemini through Google AI Studio's OpenAI-compatible endpoint | Owner answer in Phase 0 session |
| Fixed model | Provisional choice: `gemini-2.5-flash-lite`; exact current free-tier availability must be revalidated before Phase 6 | Owner requested an exact current Flash/Flash-Lite model; Google AI docs returned HTTP 429 during this audit |
| Key availability | No key yet. The owner will create one in Google AI Studio before Phase 6. No key is committed. | Owner answer in Phase 0 session |
| Budget | `$0` paid spend. Free-tier Google AI Studio calls are allowed; stop and ask if free-tier limits block an experiment. | Owner answer in Phase 0 session |
| Embeddings/reranker | Local models only; no paid embedding API | Owner answer in Phase 0 session |
| Runtime OS | Ubuntu under WSL2; use `python3` and the repository `.venv` | Owner answer in Phase 0 session |
| Training environment | Google Colab free GPU for Phase 5 | Owner answer in Phase 0 session |
| Data policy | Only public documents may be sent to an external API | Owner answer in Phase 0 session |

## Provider verification

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

- Keep `GEMINI_API_KEY` out of source control and `.env.example` values.
- API calls are not made in CI.
- Later evaluation-only LLM/API-embedding calls must be cached under `.cache/`
  by model and prompt hash; errors are never cached and cost is recorded.
- Add request throttling and exponential-backoff handling before enabling the
  provider adapter for an experiment.
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
