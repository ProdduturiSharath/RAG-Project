# Evidence RAG

Evidence RAG is an enterprise-oriented retrieval service for manuals,
contracts, and other long-form knowledge sources. The project is intentionally
split into two halves:

1. **Ingestion and indexing** turns parsed source sections into stable,
   structure-aware chunks and writes dense and sparse representations through
   small adapter ports.
2. **Async retrieval and answering** runs scoped hybrid search, second-stage
   reranking, parent expansion, ACL filtering, and grounded answer generation.

This first vertical slice runs locally without a provider key. Its hashing
encoder, in-memory index, and extractive answerer are honest development
adapters rather than fake claims of semantic understanding. They make the
interfaces testable before Pinecone and a hosted LLM are connected.

## What is already here

- Stable document/version/content-hash identities for idempotent ingestion.
- Markdown-aware and section-aware recursive-style chunking with overlap.
- Page, section-path, parent/child, and source metadata on every chunk.
- BGE-small dense embeddings, Postgres full-text search, and a true BM25 baseline.
- RRF or normalized weighted fusion followed by a configurable cross-encoder;
  token overlap remains an explainable baseline.
- Deterministic none, explicit, and auto product-version scope with ambiguity
  reporting and per-stage query traces.
- Document-level principal/group ACL checks before ranking results.
- A strict evidence prompt builder and an abstaining local answerer.
- JSON query responses with score components and citations.
- Server-Sent Events at `/v1/query/stream` for token-by-token delivery.
- Optional local text and PyMuPDF page parsers.
- A small labeled evaluation harness reporting Recall@K, MRR, and visible
  retrieval misses.
- Optional Pinecone hybrid-index and OpenAI-compatible streaming adapters that
  are loaded only when their extras are installed.

## Run locally

On Ubuntu/WSL2, create a virtual environment, install the project, and start
the API:

```bash
sudo apt install python3-venv  # once, if ensurepip is unavailable
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
uvicorn rag_service.api.app:app --reload
```

PowerShell remains supported on Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,documents]"
uvicorn rag_service.api.app:app --reload
```

The service starts at <http://127.0.0.1:8000>. The Swagger UI is at
<http://127.0.0.1:8000/docs>.

## Try the vertical slice

Ingest a small document:

```bash
curl -X POST http://127.0.0.1:8000/v1/documents \
  -H 'Content-Type: application/json' \
  -d '{"document_id":"ops-manual","version":"2026-01","source":{"uri":"ops-manual.pdf"},"sections":[{"heading":"Maintenance","level":1,"page_number":12,"text":"Replace filter SKU-994X every 12 months."}]}'
```

Ask a question:

```bash
curl -X POST http://127.0.0.1:8000/v1/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"When should SKU-994X be replaced?"}'
```

The response contains the answer, citations, ranked evidence, score
components, and an explicit `abstained` flag. The local answerer refuses to
answer when it cannot find a meaningful exact-term match.

## Test without third-party packages

The provider-independent core has a standard-library test path:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The FastAPI and optional document adapters are declared in `pyproject.toml`.
For hosted integrations, install `.[vector-store,llm]` and inject credentials
through the runtime environment rather than committing them.

## Next production increments

The next changes should be made behind the existing ports rather than inside
the API handlers:

1. Add a Pinecone hybrid index adapter and a durable document/job store.
2. Add a real embedding provider plus a corpus-fitted sparse encoder.
3. Evaluate the Phase 2 cross-encoder and parent/context expansion on the
   Phase 3 benchmark.
4. Add OCR/table extraction and Confluence ingestion workers.
5. Add a provider-backed streaming generator, OpenTelemetry traces, and a
   retrieval evaluation set covering identifiers, tables, multi-hop questions,
   conflicting versions, and unanswerable queries.

The current harness covers Recall@K, MRR, and retrieval misses. It should be
extended with nDCG, citation precision, groundedness, abstention accuracy,
p95 latency, and cost per request before the system is described as
production-ready.
