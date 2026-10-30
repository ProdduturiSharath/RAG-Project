# Evidence RAG

Evidence RAG is an evidence-first, version-aware retrieval service for long-form
technical documentation. The project thesis is:

> On large, versioned documentation, where does retrieval fail—exact
> identifiers, tables, authorization, or wrong versions—and how much does each
> fix recover, measured on a benchmark?

## Findings first

The strongest measured result is security and retrieval behavior, not a claim of
production-scale semantic quality:

- Phase 7 Study A measured **zero ACL leakage** under forced PostgreSQL RLS and
  application ACL comparison.
- Phase 7 Study B used pgvector 0.8.7 HNSW and measured **recall@10 = 1.000**
  for both `iterative_scan=off` and `strict_order` on its selective benchmark.
- The final isolated application target contains the complete public manual
  corpus: **32,719 active chunks** across `pg-15`, `pg-16`, and `pg-17`, with
  **32,719 valid BGE-small vector links** and **15,148 verified 384-dimensional
  vectors**. A separate three-chunk private ACL fixture is used only for
  authorization tests.
- The read-only recovered evaluation baseline remains separate: it contains
  **32,719 active chunks**, **20,756 vector-linked chunks**, and **9,083 verified
  vectors**. It is not the final application database and is never a mutation
  target.
- The isolated Phase 8 benchmark measured deterministic demo ingestion at
  **174.500 ms p50 / 178.326 ms p95** and read-only query latency at
  **27.367 ms p50 / 28.967 ms p95**, at **$0.00 API cost**.
- The local extractive path is intentionally honest: it returns verbatim
  evidence excerpts and exposes citation/support state rather than pretending
  to be an LLM.

Results and methodology are recorded in `results/phase*.json`,
`results/phase*_table.md`, `results/final_runtime_acceptance_20261030.md`, and
`docs/phase*_findings.md`.

## What is implemented

- Deterministic, structure-aware section/chunk ingestion with stable document,
  version, lineage, parent, source, and content-hash identities.
- PostgreSQL persistence with transactional revisions, ACL filtering before
  ranking, leased jobs, sparse search, pgvector embeddings, HNSW indexing, and
  durable query traces.
- Dense/sparse/hybrid retrieval, RRF or weighted fusion, reranking, parent
  expansion, explicit/automatic version scope, and per-stage latency traces.
- Strict HS256 JWT claim validation, principal/group authorization, request
  limits, rate limiting, timeouts, prompt-injection sanitization, quote checks,
  and per-claim support state.
- JSON and SSE query APIs, trace inspection/summary endpoints, a deterministic
  isolated demo seed, and a Streamlit findings-first UI.
- Phase 8 demo packaging with a dedicated database/volume, deterministic hash
  vectors, extractive generation by default, and no hidden provider call.

## Recovery provenance boundary

The recovered `evidence_rag_eval.public` database is intentionally treated as a
read-only evaluation baseline. Its current state is:

| Item | Count | Meaning |
|---|---:|---|
| Active chunks | 32,719 | Full surviving Phase 4 corpus |
| Sections | 23,946 | Reconstructed section records |
| Product versions | 3 | `pg-15`, `pg-16`, `pg-17` |
| Verified dense vectors | 9,083 | Loaded from the Phase 5 NumPy artifact |
| Vector-linked active chunks | 20,756 | Dense-searchable recovered subset |
| Active chunks without verified vectors | 11,963 | Not silently re-encoded |

The Phase 4/5 schemas, `evidence_rag_recovery_20261028`, and the former public
rows in `public_pre_recovery_20261029` are preserved. The recovered candidate
does not claim the original document IDs, timestamps, ACL semantics, jobs,
traces, or missing vector values were exactly restored.

## Run the final application

The final runtime uses the existing PostgreSQL 17.11 container and its
`evidence_rag_full_app_5d34bd5a2530` database. It does not start, recreate, or
remove a PostgreSQL service. The API and worker use CPU BGE-small, the CPU
cross-encoder reranker, and DeepSeek Flash. `.env` must contain a non-empty
`DEEPSEEK_API_KEY` and the verified host cache path.

```bash
docker compose --env-file .env -f docker-compose.yml up -d --build api worker ui
```

- API: <http://127.0.0.1:18010/docs>
- Streamlit UI: <http://127.0.0.1:18511>
- Final target database: `evidence_rag_full_app_5d34bd5a2530`
- Host cache mounted read-only: `/home/sharath/.cache/huggingface`
- Canonical Dockerfile build verified for `api`, `worker`, and `ui`; no patch
  image workaround remains.
- Streamlit AppTest verified live answer, version, citations, claim support,
  stage latency, and cost-ledger rendering with zero UI errors.
- The six acceptance cases were re-run through the canonical API. Every final
  DeepSeek trace persists token usage, provider latency, attempt count, and a
  positive USD estimate; the complete ledger is in
  `results/final_runtime_acceptance_20261030.md`.

Do not use `down -v` or `--remove-orphans` for this stack. The final Compose
file attaches to the existing `evidence-rag_default` network, while the demo
uses its own Compose file, project, ports, and volume.

## Run the isolated demo

Use `.env.demo` and `docker-compose.demo.yml`. Docker Compose uses
`evidence_rag_demo` and the dedicated
`evidence_rag_demo_pgdata` volume. It never seeds the recovered evaluation
databases.

```bash
cp .env.example .env.demo
# Replace POSTGRES_PASSWORD and RAG_JWT_SECRET with local values.
bash scripts/demo_up.sh
```

- API: <http://127.0.0.1:8000/docs>
- Streamlit UI: <http://127.0.0.1:8501>

If a host port is already occupied, use different host bindings without changing
the container ports:

```bash
RAG_DEMO_ENV_FILE=.env.demo \
RAG_DEMO_POSTGRES_PORT=15432 RAG_DEMO_API_PORT=18000 RAG_DEMO_UI_PORT=18501 \
  bash scripts/demo_up.sh
```

The demo seed is deterministic and uses `hash-v1` vectors; it does not run
PyTorch/SentenceTransformer inference. To seed an empty demo database directly:

```bash
PYTHONPATH=src .venv/bin/python scripts/seed_demo.py --create \
  --database-url postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_demo
```

The seed refuses to overwrite an existing schema.

## API example

The API requires an HS256 bearer token. Set the same local secret in the API and
token generator:

```bash
export RAG_JWT_SECRET='replace-with-a-local-secret-of-at-least-32-bytes'
TOKEN="$(python - <<'PY'
import os, time, jwt
now = int(time.time())
print(jwt.encode(
    {"sub": "demo", "groups": [], "roles": ["admin"], "iat": now, "exp": now + 3600},
    os.environ["RAG_JWT_SECRET"], algorithm="HS256"
))
PY
)"
curl -X POST http://127.0.0.1:8000/v1/query \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"query":"What does WAL protect?","generation_mode":"extractive"}'
```

The response includes ranked matches, verbatim citations, claim support state,
version scope, generation mode, and a persistent `trace_id`. Inspect the trace
and cost ledger with `/v1/traces/{trace_id}` and `/v1/traces/summary`.

## Reproduce checks safely

PostgreSQL tests create and destroy one uniquely named disposable database. They
must receive only the maintenance database URL; the fixture owns the generated
`RAG_TEST_DATABASE_URL` and exact `RAG_TEST_RUN_DATABASE` values.

```bash
RAG_TEST_ADMIN_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres \
RAG_DENSE_MODEL=hash-v1 RAG_RERANKER_MODEL=token-overlap \
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
.venv/bin/pytest -q -s
```

The final safe local run produced **288 passed** and dropped its generated
`rag_test_*` database. Hash/token-overlap adapters are used for this check so
the verification run does not initialize or encode with CPU transformer models.

Phase 8 benchmark:

```bash
RAG_PHASE8_ADMIN_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres \
PYTHONPATH=src bash scripts/phase8_eval.sh
```

The benchmark mutates only a temporary `rag_test_phase8_*` database and uses
`default_transaction_read_only=on` for latency queries.

Other checks:

```bash
.venv/bin/ruff check .
.venv/bin/mypy .
git diff --check
```

## Phase findings

| Phase | Measured finding |
|---|---|
| 4 | The benchmark corpus and evaluation harness report Recall@K/MRR and visible retrieval misses; source and split provenance are recorded under `data/` and `results/`. |
| 5 | Test nDCG@10 means were BM25 `0.5529033993`, recommended baseline `0.5715765760`, fine-tuned BGE-small `0.5697756181`, BGE-base `0.5804896518`, and Snowflake `0.5894004897`; these point estimates do not establish a fine-tuning win. |
| 6 | On the frozen 60-question subset, extractive correctness proxy was `0.2833`, extractive-verified `0.3167`, LLM-unverified `0.6167`, and LLM-verified `0.5167`; these are lexical/proxy measures, not independent semantic judgments. |
| 7 | Zero ACL leakage in Study A; HNSW confirmed in Study B; recall@10 `1.000` in both iterative modes. |
| 8 | Deterministic isolated-demo ingestion/query latency and persistent trace/cost observability are measured in `results/phase8_results.json`. |

## Negative findings and limitations

- The recovered corpus is not an exact database restoration. Do not infer
  original IDs, timestamps, ACL history, jobs, or traces from it.
- Dense-vector coverage is partial; the application must expose the boundary
  rather than imply all 32,719 chunks are vector-searchable.
- The Phase 8 demo uses deterministic hash vectors for zero-cost reproducibility;
  they are an offline baseline, not a semantic embedding quality claim.
- The installed `pg_dump` is PostgreSQL 15.19 while the server is PostgreSQL
  17.11. No compatible PostgreSQL 17 client was available, so a logical dump
  could not be created in this environment. Canonical read-only manifests were
  used instead and are not equivalent to a logical dump.
- Docker/Compose startup and the final API/UI runtime were verified on the
  Docker-capable host. The final runtime uses ports 18010/18511; the preserved
  demo uses ports 15432/18000/18501.
- The UI dependency is optional; install `.[ui]` or use the Docker image.
- Rate limiting is process-local, and production key rotation/asymmetric JWT
  deployment remain outside this local phase.

## Scope decisions and removal candidates

The project keeps hash, in-memory, extractive, and token-overlap adapters as
named test/offline baselines. The hosted provider remains opt-in and is never
called by the Phase 8 demo or verification commands. The old Phase 7 fallback
that substituted Phase 4/5 artifacts for a missing public schema was removed so
the benchmark now proves retrieval from the actual `public` schema.

See `docs/PLAN.md`, `docs/status.md`, and the phase findings for deviations,
uncertainties, mutation results, dataset/model cards, and remaining production
work.
