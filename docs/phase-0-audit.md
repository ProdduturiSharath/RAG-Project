# Phase 0 audit

## README claim verification

Status meanings: **verified** means supported by source and a passing local
check; **unverified** means source exists but no end-to-end or external check
was available; **false** means the wording overstates what the repository does.

| README claim | Status | Evidence and command output |
| --- | --- | --- |
| Two halves: ingestion/indexing and async retrieval/answering | verified | `git ls-files src/rag_service` shows `ingestion`, `retrieval`, `generation`, `application`, and `api` packages; the 8-test baseline passed. |
| Runs locally without a provider key | verified, local-only | `.venv/bin/python -c "from rag_service.api.app import create_app; print(create_app().title)"` prints `Evidence RAG API`; the wiring uses hash, memory, and extractive adapters. |
| Hash encoder, in-memory index, and extractive answerer are honest development adapters | verified | `api/container.py` wires `HashEmbeddingEncoder`, `InMemoryHybridIndex`, and `ExtractiveAnswerGenerator`; no provider key is read on that path. |
| Stable document/version/content-hash identities for idempotent ingestion | verified with qualification | `ingestion/chunking.py` and `ingestion/pipeline.py` provide deterministic IDs and a process-local retry cache. It is not durable idempotency. |
| Markdown-aware and section-aware recursive-style chunking with overlap | verified with qualification | `test_markdown_headings_become_section_paths` and `test_windows_keep_overlap_and_stable_ids` pass. The code is structure-aware; it is not a recursive tokenizer implementation. |
| Page, section-path, parent/child, and source metadata on every chunk | verified | `domain/models.py` and `ingestion/chunking.py` carry these fields; chunking tests cover page and section metadata. |
| Dense plus BM25-style sparse vectors behind replaceable ports | verified with qualification | `retrieval/encoders.py`, `ingestion/ports.py`, and `IngestionPipeline` implement both. The default app fits no corpus IDF, so this is a development BM25-style encoder, not Postgres BM25. |
| Candidate retrieval followed by explainable exact-token reranking | verified | `retrieval/service.py` calls the index then `TokenOverlapReranker`; retrieval tests pass. |
| Document-level principal/group ACL checks before ranking | verified after Phase 0 test strengthening | `InMemoryHybridIndex._matches` filters eligible records before scoring; dedicated principal, group, and candidate-limit tests catch the three hand mutants. |
| Strict evidence prompt and abstaining local answerer | verified with qualification | `generation/prompting.py` contains evidence-only instructions and `test_generator_abstains_without_matching_evidence` passes. Prompt output has no dedicated snapshot test yet. |
| JSON query responses with scores and citations | unverified end-to-end | `api/schemas.py` and `/v1/query` implement the response, but the repository has no API client test. |
| SSE at `/v1/query/stream` | unverified end-to-end | `api/app.py` implements the route; no streaming integration test exists. |
| Optional local text and PyMuPDF page parsers | verified with qualification | `ingestion/parsers.py` contains both. PyMuPDF execution is not covered unless the optional extra is installed. |
| Labeled evaluation harness reporting Recall@K, MRR, and visible misses | verified as a primitive, not a benchmark | `evaluation/retrieval.py` computes the fields and the evaluation test passes. There is no dataset, result artifact, confidence interval, or CLI metric runner yet. |
| Optional Pinecone and OpenAI-compatible streaming adapters | verified as unverified adapters | Both modules exist and lazy-import their optional clients; Pinecone is tested against a fake only and the LLM adapter has no live test. |
| PowerShell and Ubuntu/WSL2 local-run instructions | verified after Phase 0 rewrite | README now has Bash/WSL2 commands and retains a Windows PowerShell path. The initial baseline README was PowerShell-only. |
| “The current harness covers …” production-readiness statement | false if read as a production benchmark | It describes code-level primitives, not a corpus-backed benchmark. The README must distinguish harness code from measured results. |

No retrieval, answer, latency, cost, or benchmark metric is reported by this
audit. The only numerical outputs above are command output and configuration
facts.

## Module inventory

| Module | Status | Notes |
| --- | --- | --- |
| `rag_service/__init__.py` | implemented | Package version. |
| `rag_service/application.py` | implemented | Use-case orchestration. |
| `rag_service/settings.py` | implemented | Phase 0 typed settings foundation. |
| `rag_service/api/__init__.py` | implemented | Package marker. |
| `rag_service/api/app.py` | implemented | FastAPI routes; integration coverage is missing. |
| `rag_service/api/container.py` | implemented | Local baseline wiring. |
| `rag_service/api/schemas.py` | implemented | Pydantic HTTP schemas. |
| `rag_service/domain/__init__.py` | implemented | Domain exports. |
| `rag_service/domain/models.py` | implemented | Immutable document/chunk/ACL values. |
| `rag_service/evaluation/__init__.py` | implemented | Evaluation exports. |
| `rag_service/evaluation/retrieval.py` | implemented | Small in-memory evaluation primitive. |
| `rag_service/evaluation/experiments.py` | implemented | Typed config hash/result provenance foundation. |
| `rag_service/evaluation/run.py` | implemented | Result-artifact CLI foundation; no benchmark runner yet. |
| `rag_service/generation/__init__.py` | implemented | Generation exports. |
| `rag_service/generation/models.py` | implemented | Generator protocol and values. |
| `rag_service/generation/extractive.py` | implemented | Named offline baseline. |
| `rag_service/generation/openai_compatible.py` | implemented | Provider adapter; no live provider validation. |
| `rag_service/generation/prompting.py` | implemented | Grounded prompt builder. |
| `rag_service/ingestion/__init__.py` | implemented | Ingestion exports. |
| `rag_service/ingestion/chunking.py` | implemented | Deterministic structure-aware chunker. |
| `rag_service/ingestion/parsers.py` | implemented | Local text and optional PDF adapters. |
| `rag_service/ingestion/pipeline.py` | implemented | Process-local ingestion pipeline/cache. |
| `rag_service/ingestion/ports.py` | implemented | Adapter protocols; shared contract suite is incomplete. |
| `rag_service/retrieval/__init__.py` | implemented | Retrieval exports. |
| `rag_service/retrieval/encoders.py` | implemented | Hash test double and local BM25-style encoder. |
| `rag_service/retrieval/memory.py` | mock-only | In-memory storage/retrieval test double, intentionally retained. |
| `rag_service/retrieval/models.py` | implemented | Retrieval filters, scores, citations. |
| `rag_service/retrieval/pinecone.py` | implemented | External adapter; fake-client coverage only. |
| `rag_service/retrieval/ports.py` | implemented | Retrieval protocols; some are speculative until second real adapters exist. |
| `rag_service/retrieval/reranking.py` | implemented | Named token-overlap baseline. |
| `rag_service/retrieval/service.py` | implemented | Async hybrid retrieval orchestration. |

There are no intentional stubs. The hash encoder, memory index, token-overlap
reranker, and extractive generator are mock/test doubles or baselines by design.

## Keep, rewrite, and drop

| Area | Decision | Reason |
| --- | --- | --- |
| Immutable domain values and deterministic IDs | keep | They support lineage, citations, and reproducible tests. |
| Hash encoder | keep as a named test double only | It cannot answer the thesis about semantic retrieval. |
| In-memory index | keep as a fixture and contract-test adapter | It is useful offline, not durable production storage. |
| Token-overlap reranker | keep as a baseline | It supplies an interpretable comparison arm. |
| Extractive answerer | keep as offline baseline | It avoids API spend and gives a no-key path. |
| Process-local ingestion cache | rewrite in Phase 1 | It is not durable, revision-aware, or atomic. |
| Pinecone adapter | rewrite or remove after Phase 1 decision | The target stack is Postgres/pgvector; current adapter has only a fake test. |
| Broad retrieval/generation ports | keep only where two real implementations remain | Remove speculative aliases and protocols if they do not gain a second implementation. |
| README feature list and PowerShell-only setup | rewrite | The README must become findings-first and work for WSL2/Docker. |
| Current evaluation primitive | keep and extend | It is a useful seed, but needs dataset validation, result files, CI gate, and thesis metrics. |
| Generated `src/evidence_rag.egg-info` | drop from source control in a cleanup task | It is stale build output and duplicates project metadata. |
