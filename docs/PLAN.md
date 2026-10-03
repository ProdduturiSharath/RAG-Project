# Evidence RAG implementation plan

## Role and project thesis

This is the working plan for the Evidence RAG project. The project thesis is:

> On large, versioned technical documentation, where does retrieval fail
> (exact identifiers, tables, wrong version), and how much does each fix recover,
> measured on a benchmark?

Every feature must serve that question. The final README opens with findings,
not a feature inventory.

## Models

- **Embedding model:** a small local model, default `bge-small-en-v1.5`, with
  `bge-base-en-v1.5` as a comparison. The hash encoder remains a named test
  double only.
- **Reranker:** a small local cross-encoder. Token overlap remains a named
  baseline.
- **LLM:** one fixed model through an OpenAI-compatible API, one fixed prompt,
  and temperature 0 for retrieval experiments.
- **Fine-tuned embedding model:** `bge-small` trained on the documentation in
  Phase 5 using a free Colab GPU. An embedding API is optional comparison arm.

## Ground rules

1. No number without a source. Metrics in documents must come from a results
   file under `results/` produced by a committed script, with config hash, seed,
   library versions, and hardware. Negative results remain in reports.
2. Use four splits: train, dev, test, blind. Tune only on dev. Test is touched
   only for final reporting. The blind set is authored by the project owner and
   is never shown to or tuned by the implementation agent.
3. Splits are by section lineage, not chunk or version. All versions of one
   lineage stay in one split. Near-duplicate text is deduplicated across splits,
   and a test fails if a lineage spans two splits.
4. Test and blind questions are human-reviewed or human-written. LLM-drafted
   train/dev questions are marked `author=llm_assisted, validated=false`.
   Headline metrics use validated questions only.
5. Verify, do not assume. Check current documentation for pgvector, Postgres,
   sentence-transformers, the LLM provider, and every model's license, price,
   and limits. Record findings in `docs/environment.md`; state uncertainty.
6. Keep hash, in-memory, token-overlap, and extractive adapters as test
   fixtures and named baselines.
7. Every storage and encoder adapter passes one shared contract suite.
8. Use plain inspectable code. Do not add agent frameworks, GraphRAG,
   LangChain, Kafka, Kubernetes, or microservices. Keep only interfaces with
   two real implementations; flag speculative abstractions for removal.
9. Make small task-sized commits with tests. Ruff, type checking, and the full
   test suite pass before each commit.
10. Windows/PowerShell and Docker must work. Keep secrets out of the repository
    and provide `.env.example`.
11. Do not commit large raw corpora. Commit fetch scripts with checksums,
    license notes, and a data card.
12. Check whether mutmut runs on this OS. If it does not, use WSL or written
    mutants. Hand-written mutants are mandatory for ACL and version scoping;
    report survivors. Every phase report includes **Things I am unsure about**.
13. Pin dependencies with a lockfile. A clean-clone script reproduces headline
    numbers.
14. Cache every LLM and API-embedding response on disk by model and prompt hash,
    record cost, never cache errors, keep `.cache/` ignored, and never call paid
    APIs in CI.
15. Stop after every phase and send a phase report. Do not begin the next phase
    until the project owner confirms.

## Phase 0: audit and foundation

- Ask and record the LLM provider/key availability, budget, OS, and Colab
  training environment in `docs/environment.md`.
- Create a branch. Run tests, lint, and type checks. Record the baseline in
  `docs/status.md`.
- Verify every README claim as verified, unverified, or false, including the
  command output. Inventory every module as implemented, stub, or mock-only.
- Hand-mutate ACL filtering after top-k, remove group checks, and ignore
  principal checks. Record which tests catch each mutant and strengthen weak
  tests.
- Use a typed `pydantic-settings` configuration system. One experiment has one
  config file; its canonical hash is stored with its result.
- Document what to keep, rewrite, and drop.

## Phase 1: data model and versioned ingestion

Use Postgres with pgvector in Docker Compose and migrations. Verify the actual
pgvector version and available HNSW, iterative-index-scan, and dimension-limit
features. Keep `product_version` (search scope) separate from `revision`
(replacement upload for one document/version).

The schema must cover documents, document versions with lifecycle status and an
active-revision partial unique index, sections with stable cross-version
lineage, text/table/code chunks, embeddings keyed by content hash and embedder,
ACL principals/groups, worker jobs using `FOR UPDATE SKIP LOCKED`, and query
traces. Ingestion parses, chunks, batches embeddings, then activates a revision
in one transaction so readers never see mixed revisions.

Chunking is structure-aware with parent/child context, whole Markdown tables,
intact code blocks, and config-driven sizes. Prefer HTML/Markdown parsers, keep
a documented no-OCR PDF path, and test no-op ingestion, new revisions, delete,
ACL-only updates, embedder/chunker changes, and mid-ingest failure recovery.

Acceptance: `docker compose up` works; a real document can be ingested, updated,
and deleted end to end; the shared contract suite passes for in-memory and
Postgres adapters.

## Phase 2: retrieval pipeline

Implement typed stages for scope/auth, dense, sparse, fusion, reranking, parent
expansion, and context assembly. Each stage writes candidates, scores, and
timings to a trace. Add local sentence-transformers adapters for bge-small and
bge-base, keep the hash double, use Postgres full text plus a true BM25
baseline, and test identifier tokenization for underscores, dots, hyphens, and
mixed case. Add a custom identifier index when default tokenization fails.

Support RRF and normalized weighted fusion, configurable cross-encoder reranking
and candidate counts, chunk and parent-child ablations, metadata-prefixed
embeddings, HNSW and GIN indexes, and deterministic version modes: none,
explicit (`exact`, `latest`, `all`), and auto with an explicit ambiguous result.
Every citation carries document, product version, revision, page, and section.

## Phase 3: corpus and benchmark

Record URL, license, retrieval date, and checksum for PostgreSQL documentation
from three major versions. Add a BEIR sanity set and later optional Kubernetes,
IETF RFC, and NIST sources only when justified. Build a diff miner, a
version-question generator and evidence validator, and a labeling tool whose
labels point to document/version/quote spans rather than chunk IDs.

The JSONL dataset records id, question, type, expected answer, evidence spans,
target version, answerability, requester, ACL allowance, split, author, and
validation. Build the required balanced question types and at least 60 owner-
written blind questions. Validate schema, evidence quotes, duplicates,
lineage-split integrity, and type balance in CI. Implement and test span
overlap matching.

## Phase 4: metrics, ablations, and error analysis

Report Recall@1/3/5/10, MRR, nDCG@10, abstention precision/recall/F1, ACL
leakage (must be zero), and per-stage latency. Define version confusion for
answer-changing questions and false exclusion on unchanged controls. Use
bootstrap confidence intervals and paired bootstrap or McNemar comparisons.

Provide `python -m rag_service.evaluation.run --config configs/<x>.yaml`, which
writes `results/<hash>.json` and a Markdown table. Run one-change ablations for
sparse/dense/hybrid fusion, rerankers and candidate counts, chunk sizes and
parent expansion, metadata prefixes, and version scope. Break results down by
question type, dump 30 worst failures per main system, and gate CI on a cached
roughly-40-question subset.

## Phase 5: fine-tune embeddings on Colab

Generate training data from train only: templated identifier queries,
cache-backed LLM questions with a manually checked sample, BM25/dense/adjacent/
cross-version hard negatives, and a false-negative guard for identical answer
spans. Supply a notebook and plain script, initialize from bge-small, use
MultipleNegativesRankingLoss, checkpoint to Drive, choose hyperparameters on
dev, run three seeds, and record GPU/runtime/library versions.

Re-embed and evaluate locally on test against off-the-shelf, prefixed,
fine-tuned, and reranked arms, including cross-version-negative ablations and
an optional cached embedding API. Evaluate BEIR/Kubernetes generalization and
forgetting. Deliver the model card and report negative results honestly.

## Phase 6: generation, verification, and abstention

Add an OpenAI-compatible streaming generator while retaining the extractive
offline baseline. The fixed prompt answers only from passages, cites document,
version, and section, names the answered version, and says “not found” when
evidence is insufficient. Verify cited quotes, strip or flag unsupported
claims, expose per-claim support, and tune calibrated abstention on dev.

On a validated 60-question subset report correctness, faithfulness, citation
precision, abstention correctness, and wrong-version answers. If an LLM judge is
used, compare it with manual labels. Record a measured model/cost decision on
dev and compare extractive/LLM and verified/unverified paths.

## Phase 7: lean security

Add JWT authentication with principals/groups from verified claims only. Test
missing, expired, and tampered tokens; ACL leakage through every response and
side channel; ACL changes and deletion; and prompt injection before and after
mitigation. Add Hypothesis subset properties for both adapters, input limits,
rate limits, and timeouts. Optionally test Postgres RLS and filtered-ANN recall
as separate measured studies.

## Phase 8: packaging and presentation

Docker Compose starts API, worker, Postgres, and a seeded demo corpus. Add a
Streamlit UI with user/version controls, citations and support state, traces,
and naive/full-pipeline comparison. Persist traces and LLM cost, benchmark
ingestion and p50/p95 stage latency, and make the README findings-first with
reproducible commands, negative results, limitations, and links to decisions,
error analysis, dataset card, and model card.

## Definition of done

- Every README number reproduces from committed scripts and configs on a clean
  clone.
- Tests, lint, type checking, and the evaluation gate pass; ACL leakage is zero.
- Ablation tables with confidence intervals, version confusion, fine-tuning
  results, error analysis, and limitations are published.
- The owner has run the blind set and its numbers are separate.
- A new user can run the demo with one command.

## Phase report format

After every phase report:

1. What was implemented (files and commits).
2. Commands to verify, with actual output.
3. Test, lint, type-check, and mutation results.
4. Metrics produced, with result paths, including bad ones.
5. Deviations from this plan and why.
6. Things I am unsure about.
7. Abstractions or code that should be removed.
