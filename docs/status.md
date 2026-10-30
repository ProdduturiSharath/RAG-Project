# Phase 0 status

## Baseline before Phase 0 edits

Baseline branch: `phase-0-audit-foundation`.

The baseline was run after creating `.venv` and installing the repository's
existing `.[dev]` extra plus `mypy` manually. It was run before the Phase 0
configuration and audit edits.

### Test command

```text
$ .venv/bin/python -m pytest -q
........                                                                 [100%]
=============================== warnings summary ===============================
tests/unit/test_evaluation.py::EvaluationTests::test_retrieval_metrics_make_misses_visible
  .../pytest_asyncio/plugin.py:1216: DeprecationWarning: 'asyncio.get_event_loop_policy' is deprecated and scheduled for removal in Python 3.16
1 warning in 0.11s
8 passed, 1 warning in 0.11s
```

### Lint command

```text
$ .venv/bin/ruff check src tests
All checks passed!
```

### Type-check command

```text
$ .venv/bin/mypy src tests
tests/unit/test_provider_adapters.py:65: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:66: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:71: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:72: error: Value of type "None" is not indexable  [index]
tests/unit/test_provider_adapters.py:73: error: Value of type "None" is not indexable  [index]
tests/unit/test_evaluation.py:20: error: Argument 2 to "EvaluationCase" has incompatible type "set[str]"; expected "frozenset[str]"  [arg-type]
Found 6 errors in 2 files (checked 36 source files)
```

The baseline test and lint results are command output, not retrieval or answer
metrics. No benchmark result exists in this baseline.

## Installed tool versions at baseline

The source command was `.venv/bin/python -m pip show pytest ruff mypy fastapi
pydantic`. The observed versions were pytest 8.4.2, Ruff 0.16.10, mypy 2.4.0,
FastAPI 0.142.2, and Pydantic 2.13.5. The lock file is the reproducible source
for the complete environment.

## Phase 0 completion checks

These are filled after the audit edits and mutation runs:

- [x] typed settings and experiment provenance pass
- [x] all tests pass
- [x] Ruff passes
- [x] mypy passes
- [x] README claim audit is committed
- [x] module inventory is committed
- [x] ACL mutants are caught by named tests
- [x] mutation tool availability is recorded
- [x] no benchmark metrics were invented

## ACL hand-mutant results

Each mutant was applied directly to the working tree, run against the named
target, and restored before proceeding. Every mutant was caught:

| Mutant | Command | Result |
| --- | --- | --- |
| Apply ACL filtering after the candidate limit | `.venv/bin/python -m pytest tests/unit/test_retrieval.py -q` | **Caught** by `test_acl_filtering_precedes_candidate_limit`: `1 failed, 3 passed`; the expected public result was empty after the bad top-1 restricted candidate. |
| Drop group authorization | `.venv/bin/python -m pytest tests/unit/test_retrieval.py::RetrievalTests::test_group_acl_is_checked_for_denied_and_allowed_groups -q` | **Caught**: `1 failed`; the allowed `operations` group returned no result. |
| Ignore principal identity | `.venv/bin/python -m pytest tests/unit/test_retrieval.py::RetrievalTests::test_document_acl_is_applied_before_ranking -q` | **Caught**: `1 failed`; `restricted` unexpectedly appeared for `bob`. |

`mutmut` is not installed in this environment: `.venv/bin/python -m mutmut
--version` returned `No module named mutmut`. Phase 0 therefore uses the
required hand-written mutants under WSL2. No mutant was left in the final tree.

## Phase 0 result artifact

The committed foundation CLI produced:

```text
$ .venv/bin/python -m rag_service.evaluation.run --config configs/phase-0-foundation.yaml
results/f53cf6e8a31fa0261e124451b1ab0a246c98447880e01300d04a224fbada28f6.json
```

This artifact has an empty `metrics` object because Phase 0 has no dataset or
benchmark. It records the config hash, seed, library versions, and hardware;
it does not invent a retrieval metric.

## Things I am unsure about

- Google AI Studio's current OpenAI-compatible endpoint, fixed Flash/Flash-Lite
  model availability, free-tier limits, and model terms could not be verified
  because the official AI documentation returned HTTP 429 in this environment.
- The current repository's Pinecone adapter is only tested against a fake client;
  no live provider behavior is claimed.
- The project has no corpus or validated benchmark, so no retrieval quality
  conclusion is warranted.

## Phase 1 post-PR-2 handoff — 2026-10-03

- PR #2 remains open and unmerged on `phase-1-postgres-versioned-ingestion`.
- Commits `a4bbf47`, `2cd61e9`, and `c0f594a` add disposable integration
  databases, atomic-revision/reader/concurrency coverage, pinned pgvector CI,
  localhost-only Compose binding, `.env` password configuration, and typed HTML
  table/code parsing.
- The two required hand mutants were each caught and restored: omitted
  supersession failed the reader atomicity test; omitted
  `document_versions_one_active` failed the unique-index test.
- Final local verification: full suite `28 passed`; integration suite `13
  passed`; Ruff and mypy passed. CI run `37120488480` passed both unit and
  integration jobs; its integration job created and dropped a `rag_test_*`
  database and reported `13 passed`.
- Clean-volume Compose restart was run twice during verification; the final
  suite was run twice in sequence and once with a seeded shuffled order.
- Live query verified PostgreSQL `17.11` with pgvector `0.8.7`; the exact
  official release URL checked was
  `https://github.com/pgvector/pgvector/releases/tag/v0.8.7`.
- Real smoke input was fetched to `/tmp/omnirush` only from PostgreSQL 17
  documentation; it produced 125 sections, 2 table chunks, and 2 code chunks.

Phase 2 implementation is complete on `phase-2-retrieval-pipeline`; final verification and PR are recorded in `docs/phase-2-report.md`.

## Phase 3 Postgres follow-up — 2026-10-04

- Postgres container `evidence-rag-postgres-1` was healthy; API and worker were
  intentionally left stopped. The separate `evidence_rag_eval` database was
  created and used for corpus ingestion.
- The table audit found 460 literal SGML table elements containing cells in
  PostgreSQL 15 and 459 parser table records/chunks. The one literal omission
  is an XSLT/HTML table inside `func.sgml` line 15106 within a code example,
  not a documentation table. The parser previously lost titled real tables;
  title-state handling was fixed and covered by a real SGML-table test.
- `scripts/corpus_metrics.py` now reports: pg-15 `7893 sections / 10741
  chunks / 459 tables / 3822 code`; pg-16 `7984 / 10877 / 467 / 3873`; pg-17
  `8069 / 10997 / 463 / 3939`.
- Eval ingestion used `bge-small-en-v1.5`: pg-15 computed 10,653 and reused
  0 embeddings in 1,135.776 seconds; pg-16 computed 1,431 and reused 9,356
  in 187.740 seconds; pg-17 computed 1,457 and reused 9,447 in 197.899
  seconds. Total embedding time was 1,521.415 seconds; artifact:
  `data/eval/ingestion_metrics.json`.
- Full suite with the disposable test database: `48 passed in 48.06s`.
  The earlier 16 skips were the 4 Postgres retrieval tests, 3 schema/job
  tests, 4 revision-atomicity tests, and 5 versioned-storage contract tests;
  all now pass. PR #4 remains open; unit and integration CI both pass.

## Phase 3 manual drafting checkpoint — 2026-10-04

This checkpoint supersedes the generated-candidate counts in the original
Phase 3 report. Branch: `phase-3-corpus-benchmark`. PR #4 has not been merged;
Phase 4 has not started. The NVIDIA API is dropped. No external API was called
and `.env` was not read. Drafting rules are saved in
`docs/question-drafting-rules.md`; read those before continuing.

### Corrected corpus refresh

- Source records: pg-15 **7,893**, pg-16 **7,984**, pg-17 **8,069**; total
  **23,946**, spanning **12,581** current lineage keys.
- Preserved **11,247** surviving assignments; assigned **1,334** new keys
  deterministically without adding blind keys. Of **662** retired keys,
  **62** retired blind keys remain reserved, keeping the original pool intact.
- Persisted split counts: train **3,814**, dev **3,808**, test **3,806**,
  blind **1,215** (12,643 assignments including the 62 retired blind keys).
- Re-mined **732** changed lineage/version pairs from **11,365** adjacent-version
  matches. Change counts: defaults **3**, parameter additions **182**, removals
  **90**, rename hints **9**, table rows added **262**, removed **186**, other
  text changes **546**. No questions were based on other text changes.
- Fixed default-change attribution: a nearby `shared_buffers` reference no
  longer steals `vacuum_buffer_usage_limit`'s default change.
- The **3 lineage tests** passed during refresh. Final audit also compared
  surviving assignments, the complete blind pool, and every saved blind passage
  against pre-session commit `45a586d`: all unchanged.
- Full corrected sources are local/ignored at
  `data/processed/source_sections.full.jsonl`. The committed compact source
  artifact contains **1,253** records, including the untouched blind passages.

### Completed batches and counts

All questions were written directly by `omnirush/gpt-6-astra` after reading
eligible passages. No question generator, template, external model, retrieval
code, or retrieval results were used for drafting. The old **198** generated
candidates and their generator were removed.

| Batch | Accepted | Discarded | Contents |
| --- | ---: | ---: | --- |
| `batch_001.json` | 25 | 0 | 12 version-specific, 5 controls, 8 unavailable |
| `batch_002.json` | 25 | 0 | 8 factoid, 8 identifier, 5 table, 2 multi-hop, 2 ACL |
| `batch_003.json` | 25 | 0 | 18 unanswerable, 6 ACL, 1 table |
| `batch_004.json` | 25 | 0 | 13 factoid, 12 identifier |
| `batch_005.json` | 25 | 0 | 14 factoid, 11 identifier |
| `batch_006.json` | 24 | 1 | 19 table, 4 identifier, 1 unavailable |

The rejected batch-006 row asked about `scram_iterations` in PostgreSQL 15:
the identifier occurs in that version's full corpus, so it cannot pass the
strict version-unavailable check. The raw draft remains in the batch for audit;
it is absent from candidates. Each batch has a `.report.json` with reasons.

| Type | Accepted | Discarded | Target | Remaining |
| --- | ---: | ---: | ---: | ---: |
| factoid | 35 | 0 | 35 | 0 |
| exact_identifier | 35 | 0 | 35 | 0 |
| table | 25 | 0 | 25 | 0 |
| multi_hop | 2 | 0 | 12 | 10 |
| unanswerable | 18 | 0 | 18 | 0 |
| acl | 8 | 0 | 8 | 0 |
| version_specific | 12 | 0 | up to 50 | up to 38 |
| unchanged_control | 5 | 0 | 25 | 20 |
| version_unavailable | 9 | 1 | 10 | 1 |

**149 accepted, 1 discarded.** Target versions are pg-15 **50**, pg-16 **45**,
pg-17 **54**. Factoid and identifier each have **17/35** paraphrased rows.
All accepted rows have `author=llm_drafted`, `drafted_by=omnirush/gpt-6-astra`,
and `validated=false`. Stable-source categories use `version_independent=true`.
These are unreviewed candidates, not a validated benchmark.

### Resume exactly here

Stopped at a context checkpoint after completing **batches 001–006**; those
batches were committed individually and pushed after batches 003 and 006.
**Next batch: `data/eval/drafts/batch_007.json`.** Remaining work is **10
multi-hop**, **20 unchanged controls**, **1 version-unavailable**, and **up to
38 version-specific** questions. No remaining source-scarcity claim has been
made: the specialized diff pool has not been exhausted. Manually screen mined
identifier additions/removals against full sources; a mention or table-position
change does not establish a feature's introduction/removal.

Do not re-import completed batches (the importer will discard duplicates).
Use the persisted split file. Do not regenerate candidates or touch the blind
pool. For new batches:

```bash
PYTHONPATH=src .venv/bin/python scripts/inspect_drafting_sources.py --help
PYTHONPATH=src .venv/bin/python scripts/import_drafts.py data/eval/drafts/batch_007.json
PYTHONPATH=src .venv/bin/python scripts/audit_drafts.py
```

### Verification at this checkpoint

- Importer checks normalized-whitespace quote matching and persists original
  quotes plus exact character offsets, full-source identifier absence, dev/test
  membership for every evidence section, stable-lineage claims, specialized
  diff provenance, distinct same-version multi-hop sources, ACL source/requester
  membership, duplicate questions, and common placeholder/vague/meta wording.
- Final audit rechecked **all 149 accepted rows** against all three full local
  versions. Summary: `data/eval/drafting_stats.json`.
- Importer tests: **13** tests included in the final suite. Full suite was run
  **once at the end: 63 passed in 9.58s**, including the disposable PostgreSQL
  database tests, with no skips. `.env` loading was explicitly disabled before
  pytest collection; offline model flags prevented model downloads:

```bash
RAG_TEST_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/postgres \
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -c \
"from rag_service.settings import Settings; Settings.model_config['env_file'] = None; import pytest; raise SystemExit(pytest.main(['-q']))"
```

- Ruff (`src tests scripts`) and mypy (`src tests`) pass. Dataset validation
  passes with no errors and four target-shortfall warnings; partial pools are
  allowed. The importer and schema never mark model-authored drafts validated.
- **Current PR #4 CI is unverified.** Querying GitHub checks would call an
  external API, prohibited by this session's instructions. The historical green
  status above applies to the previous commit, not this checkpoint. Local checks
  pass; a future session with permission to query GitHub must check the new SHA.

### Labeling commands

```bash
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py review --candidates data/eval/candidates.jsonl --output data/eval/reviewed.jsonl
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py write --source data/eval/source_sections.jsonl --splits data/eval/splits.json --output data/eval/blind.jsonl
```

## Phase 3 drafting completion — 2026-10-05

**All requested drafting is complete on `phase-3-corpus-benchmark`.** This
completion supersedes the batch-007 resume instructions and incomplete counts
above. Batches **001–009** are done; there is no remaining drafting work.
PR #4 remains open and unmerged. Phase 4 has not started. No model/LLM API was
called, no question generator was used, and `.env` was not read. Git and `gh`
were permitted by the continuation instructions.

### Final pool

| Type | Accepted | Import-discarded | Removed after import |
| --- | ---: | ---: | ---: |
| factoid | 35 | 0 | 0 |
| exact_identifier | 35 | 0 | 0 |
| table | 25 | 0 | 0 |
| multi_hop | 12 | 0 | 1 |
| version_specific | 50 | 0 | 0 |
| unchanged_control | 25 | 0 | 0 |
| version_unavailable | 10 | 1 | 0 |
| unanswerable | 18 | 0 | 0 |
| acl | 12 | 0 | 0 |
| **Total** | **222** | **1** | **1** |

- ACL: **8 denied, 4 allowed**. Allowed cases use `alice` or `bob` and the
  explicit `docs-admins`/`sre` policy in `data/acl_demo.yaml`. The importer derives
  and verifies `acl_allowance` from that policy, rather than marking every ACL
  requester denied. All ACL questions use restricted stable source sections.
- Multi-hop: removed the independent `plan_cache_mode` + `effective_cache_size`
  question. Rewrote the original GEQO question to ask for
  `current_setting('geqo_threshold')`: identify the setting from its behavior,
  then supply that setting as the function argument. All **12** candidates now
  ask one connected question and record their dependency in `reasoning_chain`.
  Two new default-ACL questions were tightened further to avoid giving away
  the object type that must be decoded from the first passage.
- Version questions and controls all carry specialized `diff_id` provenance;
  new sources include changed aggregate Partial Mode support, the
  `force_parallel_mode`/`debug_parallel_query` rename, and added parameters,
  functions, and catalog rows. **All targets reached; no filler or other-text
  diff padding, and no source-scarcity shortfall.**
- The one final import discard remains the batch-006 `scram_iterations` item,
  because its identifier occurs in the requested pg-15 corpus. The batch-007
  first attempt had one source-version mismatch, corrected to pg-15 and retried
  successfully; its report retains that correction history without counting
  already accepted rows as duplicates.
- Target-version counts: pg-15 **79**, pg-16 **81**, pg-17 **62**. Factoid and
  exact-identifier still each have **17/35** behavior-paraphrased questions.
- Every candidate is `author=llm_drafted`, `drafted_by=omnirush/gpt-6-astra`,
  `validated=false`; these are ready for human review, not human-validated gold.

### Continuation batches

| Batch | Accepted | Final discarded | Contents |
| --- | ---: | ---: | --- |
| `batch_007.json` | 25 | 0 | 11 connected multi-hop, 4 allowed ACL, 10 version-specific |
| `batch_008.json` | 25 | 0 | 25 version-specific |
| `batch_009.json` | 24 | 0 | 20 controls, 3 version-specific, 1 version-unavailable |

Each batch was written manually, imported, and committed; origin was pushed
after batch 009. Explicit handwritten corrections are retained in
`data/eval/drafts/revisions.json`.

### Gold-version bookkeeping

All **119 version-independent rows** now store their primary `lineage_key`
and `gold_versions`. Full text and block kinds are compared character-for-
character within each lineage across all source versions, using
`src/rag_service/benchmark/gold.py`. Each evidence span stores its own gold
versions; multi-hop rows store the intersection for both evidence lineages.
The importer calculates these lists, the validator verifies them, and a new
unit test rejects an incomplete list. Equivalent sources are included in the
committed compact artifact so CI can verify them offline. That artifact now
contains **1,336** records; full ignored local corpus remains **23,946** records.

The bookkeeping script can refresh metadata without producing questions:

```bash
PYTHONPATH=src .venv/bin/python scripts/refresh_draft_metadata.py
PYTHONPATH=src .venv/bin/python scripts/audit_drafts.py
PYTHONPATH=src .venv/bin/python scripts/validate_dataset.py
```

No splits or blind passages were changed in this continuation. The full-source
audit confirms both their equality to commit `45a586d` and exact evidence spans
for every one of the **222** accepted rows. Counts and provenance summary:
`data/eval/drafting_stats.json`.

### Final verification

- Focused importer tests during iteration: **14 passed**, including the new
  gold-version test. Full suite run once at the end: **64 passed in 19.68s**,
  including disposable PostgreSQL tests, no skips. Same offline flags and
  explicit `Settings.model_config['env_file'] = None` as the command above.
- Ruff (`src tests scripts`) and mypy (`src tests`) pass.
- Dataset validator: **222 records, zero errors, zero warnings**.
- PR #4 checks queried with `gh`: unit and integration **PASS** for batch-009
  commit `2d5d432`, run `37273178459`. The final handoff commit is pushed and
  its head checks are checked again before the final response.

### Next action: human labeling

```bash
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py review --candidates data/eval/candidates.jsonl --output data/eval/reviewed.jsonl
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py write --source data/eval/source_sections.jsonl --splits data/eval/splits.json --output data/eval/blind.jsonl
```

## Phase 3 cleanup — 2026-10-05

The owner approved the earlier section-family migration, including its
one-time blind correction, and knows of no additional exposure history.
Applied on `phase-3-corpus-benchmark` from baseline `cee8890` with a pre-write
guard: **all projected numbers matched**. This supersedes the earlier promises
of unchanged lineage-level assignments/blind membership; normal refreshes now
preserve **section-family** decisions.

### Actual migration and preservation

| Item | Actual |
| --- | ---: |
| Changed existing lineage assignments | 4,709 |
| Candidate rows whose split changed, test → dev | 32 |
| Candidates retained | 222 |
| Candidate dev / test | 118 / 104 |
| Accepted human reviews retained unchanged | 6 (2 dev / 4 test) |
| Blind lineage keys | 3,497 |
| Blind families | 1,071 (1,017 current + 54 retired-only) |
| Mixed-split families | 0 |

- Split assignment counts: train **1,896**, dev **4,985**, test **2,265**, blind
  **3,497**. All **62** retired reservations remain unchanged.
- Grouped **12,581** current keys into **6,653** section families from the full
  **23,946** local source records, not just the compact artifact; **115** current
  families have no prose. Blocks use `metadata.section_lineage`, other records
  stable section identity. No titles are used for splitting.
- Transitive connections across multi-hop questions resolve as **five**
  multi-family components. Candidate/review components stay dev/test, with dev
  preferred on conflicts. Historical drafted/generated questions are included
  in the exposure inventory, including discarded/removed drafts.
- Excluded **19** exposed old blind families (**21** blind keys) and promoted
  **2,303** sibling keys of retained blind families. No previously non-blind
  family was added as a new blind family. **148** recorded exposed families are
  excluded from blind. Exposure outside recorded history remains unverifiable;
  the owner confirms no additional history and no private blind questions.
- Candidate preservation checked once during migration: all IDs, questions,
  answers, evidence, gold versions, flags, and other payload fields are equal
  to baseline after excluding only `split`. Exactly 32 split fields changed.
  All six reviews' bytes were preserved, and `reviewed.jsonl` remains untracked.
- `data/eval/section_families.json` commits full metadata coverage (including
  reservations), not the full corpus. CI checks every family assignment,
  connected component, exposed-family exclusion, and compact source identity.
  `data/eval/split-migration.json` records approval, baseline/full-source/review
  fingerprints, history provenance, and every assignment change/reason.
- Builder, importer, validator, and audit now enforce family isolation. The
  old `45a586d` equality assertions are replaced with preservation of the
  approved family baseline; new blocks/versions inherit the existing split.

### Review flags and final-gold eligibility

Rejected rows now save `review_status=rejected, validated=false`; accepted rows
save `review_status=accepted, validated=true`. `is_final_gold` and validator
`--final-gold` mode require **both** explicit acceptance and validated true, so
legacy rejected rows marked validated true remain ineligible. Ordinary
candidate validation still allows unreviewed drafts. Future owner-authored blind
rows have explicit accepted status. The six existing accepted reviews were
not rewritten; all 222 model candidates remain unvalidated.

```bash
PYTHONPATH=src .venv/bin/python scripts/validate_dataset.py
PYTHONPATH=src .venv/bin/python scripts/validate_dataset.py --dataset data/eval/reviewed.jsonl --final-gold --allow-incomplete
```

### Bounded read-only parser findings

Full findings: `docs/phase-3-parser-impact-audit.md`. Inspected the **11 flagged
candidates**, **six extra candidates**, and **three table-title examples**.
Missing “see” references are cosmetic for the 11 selected answers. Neighboring
gaps lose real meaning: track_counts, JIT setting names/EXPLAIN, VACUUM/ANALYZE,
and application_name disappear from defining or explanatory sentences.

Table titles overwrite section titles and parent paths. pg_stat_activity's
13 records get the last wait-event table title; WAL Settings becomes
synchronous_commit Modes; pg_subscription becomes pg_subscription Columns.
Explicit family identities survive. A synthetic read-only example demonstrates
that lost parent/title keywords can affect title-based ACL classification;
no allowance flip was found for the current ACL candidates' restricted ancestor
paths in this bounded audit.

All **six accepted answers remain supported**. The two pg_subscription reviews
should have their context metadata revisited after parser repair; no changed
answer or rejection is indicated now. Recommend a separate repair to distinguish
table/section titles, preserve parent identity, and render meaningful xref
labels. **No parser repair, corpus regeneration, ingestion or embedding run**
was performed in this cleanup. No model API or `.env` was accessed.

### Verification

- Full offline suite run **once: 69 passed in 9.32s**, including disposable
  PostgreSQL tests, no skips. `.env` loading was disabled before collection and
  `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` prevented model downloads.
- Dataset validation: **222 rows**, **zero errors/warnings**, **zero final-gold
  rows**. Accepted-review validation with `--final-gold --allow-incomplete`:
  **six rows**, all eligible, **zero errors/warnings**.
- Full-source family/evidence audit passes; the compact CI source artifact is
  **3,618 records**. Candidate/review payload preservation was checked once at
  migration, and the five new focused tests cover family/block/transitive/CI
  isolation plus review rejection/acceptance and explicit blind acceptance.
- Ruff initially found two overlong lines in scripts; formatting only was
  corrected, then lint/type checks repeated. Ruff (`src tests scripts`) and
  mypy (`src tests`) pass.
- PR #4 remains unmerged; Phase 4 has not started. Parser repair is a separately
  recommended follow-up, not a blocker to completing this cleanup.

## Phase 3 identity-preserving parser repair — 2026-10-05

The owner approved the bounded repair and an identity-compatibility strategy
after the initial dry run failed its guard. The legacy collector remains the
authority for every existing section ID, lineage key, block ordinal, and
family identity. A parallel display collector renders xref labels, keeps
explicit link/parameter text, and separates table captions from section titles
and parent paths. Existing records carry corrected text/title/path and the
legacy heading path as metadata; captions are a separate field. No other
structural parser behavior was changed.

### Guards and formerly empty records

- **All guards passed before artifact application:** existing identities and
  split assignments unchanged; all 222 candidate IDs, questions, answers,
  primary/evidence lineage keys unchanged; zero mixed families; no old blind
  key left blind. Candidates remain dev **118** / test **104**, blind keys
  **3,497**. All 12 ACL candidates still have a restricted heading ancestor
  (**8 denied, 4 allowed**).
- All existing family-manifest entries remain equal to the pre-repair entries.
  The manifest source fingerprint and provenance reflect repaired content;
  migration provenance records the approved extension (zero added assignments).
- The repaired rendering discovers **607** previously empty record instances,
  with character lengths **15–116**: **419 under 50**, **167 at 50–99**,
  **21 at 100–299**, **0 at 300–1499**, **0 at 1500+**. All **607** contain
  cross-references only, so the owner's filter excludes all of them, including
  the 188 that pass the length cutoff. No new records are indexed or assigned.
  All 607 receive collision-checked `xref-restored-*` identities in the impact
  inventory, but excluded records do not enter the index or assignment file.
  A qualifying restored record inherits its existing family or uses the
  builder's deterministic split rule; existing siblings are unaffected.
- This bounded sample provides no evidence to relax the 50-character guess:
  length alone would retain 188 reference-only navigation entries. The
  reference-only rule is what excludes them correctly here.
- Full indexed corpus remains pg-15 **7,893**, pg-16 **7,984**, pg-17 **8,069**
  records. Compact artifact remains **3,618** records, with repaired text and
  display metadata. Full corpus is still ignored/local, never committed.

### Dry-run and real eval ingestion

Recorded dry-run: `data/eval/parser-repair-impact.json`. The earlier unguarded
prototype predicted 5,240 embeddings; after excluding all 607 reference-only
records, the identity-preserving run predicted **5,040**, below 10,000.

| Version | Changed existing chunk text | Added windows | Changed display-metadata chunks |
| --- | ---: | ---: | ---: |
| pg-15 | 3,313 | 36 | 3,405 |
| pg-16 | 3,413 | 35 | 3,506 |
| pg-17 | 3,496 | 33 | 3,521 |

Re-ingested the guarded full artifact only into **evidence_rag_eval**, using
cached local `bge-small-en-v1.5` with offline model flags and content-hash reuse.
The running Postgres container initially had no attached network/published
host port; reconnected its existing Compose network and used a temporary local
forwarder on port 55432. No `.env` or model API was accessed. The forwarder is
removed after final local verification; no server was re-created or re-ingested
into a test database.

| Version | Documents | Sections | Chunks | Table | Code | Computed | Reused | Embedding seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pg-15 | 1 | 7,893 | 10,777 | 459 | 3,822 | 3,332 | 7,363 | 348.672 |
| pg-16 | 1 | 7,984 | 10,912 | 467 | 3,873 | 844 | 9,984 | 117.327 |
| pg-17 | 1 | 8,069 | 11,030 | 463 | 3,939 | 864 | 10,079 | 125.178 |

**5,040 embeddings computed; 591.178 seconds total encoding time**. These are
measured encoding calls, not total job wall time. Artifact:
`data/eval/parser_repair_ingestion_metrics.json`; the original ingestion metrics
remain available for comparison. Corrected heading paths/captions are stored
with ingestion metadata; embeddings remain text-only, reusable by content hash.

### Evidence and owner re-confirmation

Exactly the **16 approved IDs** have changed evidence quote text. All other
quote strings are identical; source offsets/heading paths were refreshed as
needed. Full old/new quotes and the list are printed in
`docs/phase-3-evidence-changes.md`, with machine-readable pairs in the impact
artifact. Questions/answers are unchanged. Full-source audit confirms source
spans, stable-version gold metadata, and family assignments.

`reviewed.jsonl` remains unchanged and untracked. Two of its accepted IDs,
`draft-257b83c46f868ef6` and `draft-2698580abdaeb4fb`, need evidence re-confirmation:
their cache/default answers are still correct. The two pg_subscription
bool/char reviews still hold, with unchanged quote text and corrected section
context. The review tool skips already-reviewed IDs in its output, so use a
separate fresh output to reconfirm only the two changed-evidence reviews:

```bash
PYTHONPATH=src .venv/bin/python scripts/label_dataset.py review --ids draft-257b83c46f868ef6,draft-2698580abdaeb4fb --output data/eval/parser-reconfirmations.jsonl
```

Choose `a` to append an explicit accepted human review with the same ID and
repaired evidence to the new file. Earlier decisions are retained in the
original file. Reusing an output containing those IDs will skip them again.

### End-of-task verification

- Dataset validation: **222 records, zero errors and warnings**. Full-source
  audit passes, including all 119 gold-version lists and all family assignments.
- Full offline suite run once: **72 passed in 15.16s**, including disposable
  PostgreSQL tests with `.env` loading disabled before collection. Three new
  SGML tests cover real parameter/command xrefs, catalog captions/parent paths,
  and filtered reference-only sections without shifting legacy sibling IDs.
- Initial Ruff check found formatting and a missing explicit zip mode; fixed
  those and completed the ID-filter regression assertions. Focused parser/review
  checks then passed **5/5**; Ruff (`src tests scripts`) and mypy (`src tests`)
  pass. Those checks were repeated only for the failures/follow-ups. Full suite
  was not repeated.
- PR #4 is checked after pushing. It remains unmerged; Phase 4 has not started.

## Phase 3 final gold closeout — 2026-10-10

The independent model audit is the validation decision for the 222 candidates:
212 accepted, 10 rejected, and 0 flagged. `data/eval/gold.jsonl` contains 212
rows, all with `review_status=accepted` and `validated=true`.

| Type | Gold rows | Human | Model audit | Owner written |
| --- | ---: | ---: | ---: | ---: |
| factoid | 34 | 0 | 34 | 0 |
| exact_identifier | 32 | 0 | 32 | 0 |
| table | 22 | 0 | 22 | 0 |
| multi_hop | 12 | 0 | 12 | 0 |
| version_specific | 48 | 4 | 44 | 0 |
| unchanged_control | 25 | 0 | 25 | 0 |
| version_unavailable | 10 | 0 | 10 | 0 |
| unanswerable | 18 | 0 | 18 | 0 |
| acl | 11 | 0 | 11 | 0 |
| **Total** | **212** | **4** | **208** | **0** |

The six historical human reviews remain untouched. Two had parser-repaired
quotes and therefore fell back to the audit; one of those was rejected. The
schema now recognizes `review_method` values `human`, `model_audit`, and
`owner_written`, while ordinary unreviewed drafts remain allowed in
`candidates.jsonl`. Final-gold validation passes with zero errors. The repaired
table representation, including intact title/path and separate caption, is in
[`dataset_card.md`](dataset_card.md).

Phase 4 reports metrics on all gold rows AND separately on human and
owner_written rows. The Phase 4 closeout host evaluation completed on
2026-10-11.

## Phase 4 implementation — 2026-10-10
- `phase-4-evaluation` is based on merged `main`; both human-review inputs are committed and all 212 gold rows rebuild byte-for-byte.
- Phase 4 closeout adds the DEV-stacked `recommended` and cross-encoder variant, paired comparisons, and JSON-driven `docs/phase4_findings.md` generation; Phase 5 has not started.
- Host Phase 4 ran with `bash scripts/run_phase4.sh --metadata-prefix --scifact`; closeout findings and aggregate reports are ready, while per-arm JSON artifacts remain local because they exceed the commit-size limit.
- `docs/phase4_findings.md` and `results/phase4_table.md` are committed; the approximately 930 MB per-arm JSON artifacts stay local. Findings regenerate with `bash scripts/run_phase4.sh --metadata-prefix --scifact`.
- `results_run1_backup/` was removed; Phase 5 has not started.
- Future sessions reuse the project-local GitHub login with `GH_CONFIG_DIR="$PWD/.gh-config" .tools/gh/gh auth status`; Git uses the ignored `.tools/git-credential-gh` wrapper configured locally.

## Phase 5 implementation — 2026-10-14
- `phase-5-finetune` adds resumable host prepare, GPU sweep/training, host evaluation, model-card provenance, and focused leakage guards.
- The prepare stage uses Postgres-first active chunks, locked Lineup A generators, deterministic 1,350-passage stratification, and a `--sample N` offline-sized generation path.
- The GPU stage uses the verified static MTEB lineup, dense/BM25 interleaved hard negatives, three BGE seeds plus Snowflake seed 1, and GPU SciFact summaries.
- Evaluation preserves ACL/scope gates, averages multi-seed metrics per question, and reports lineage-bootstrap CIs for strict, windowed, and section-family recall.

## Phase 5 host evaluation closeout — 2026-10-24

- `bash scripts/phase5_eval.sh` completed with exit code 0 in 355.20 seconds.
  The earlier unoptimized run had not finished after approximately three hours;
  that interrupted run is not a completed timing baseline.
- Reused the Race Engineering GPU outputs through the ignored `phase5_outputs`
  symlink and all 127,577 existing rows in `phase5_1efc7486ead74d968f1e.vectors`.
  No models were retrained, GPU work repeated, or artifacts/schema deleted.
- The evaluator caches exact ordered BM25 subsets and sparse query scores,
  uses float32 matrix-vector dense scoring with deterministic cutoff ties, and
  reports question progress and stage timings. ACL and version filtering remain
  before top-k. Text-hash fallback is preserved and computed once per chunk.
- Generated `results/phase5_results.json`, `results/phase5_table.md`, and
  `docs/phase5_findings.md`: 52 arm/split summaries and 120 paired comparisons
  from 115 dev and 97 test questions (82 test questions have nDCG scores).
- Source: `results/phase5_results.json`. Dev selected
  `dense-Qwen_Qwen3-Embedding-0.6B`; all seven fine-tuned alpha selections were
  0.25. Test nDCG@10 means: BM25 0.5529033993, recommended baseline
  0.5715765760, fine-tuned recommended BGE-small 0.5697756181, BGE-base
  0.5804896518, and Snowflake 0.5894004897. These point estimates alone do not
  establish a fine-tuning win; use the paired confidence intervals and limits.
- Verification: 154 Phase 5 tests passed; full offline suite 221 passed,
  16 skipped; `ruff check .` passed; full `mypy .` passed with 0 errors across
  107 source files after typing fixes in the corpus/ingestion utility scripts.
- Results and edits remain local for review; no commit/push or Phase 6 run.

## Phase 6 generation / verification closeout — 2026-10-28

- Phase 5 commit `80b494b` was pushed and merged into `main` with no-FF merge
  `549375e`; `main` was pushed and `phase-6-generation` created from it.
- Implemented the fixed `deepseek-flash` streaming provider at
  `https://api.deepseek.com/chat/completions`, reading only `DEEPSEEK_API_KEY`.
  Explicit `thinking.type=disabled`, temperature 0, 45s total attempt deadline,
  throttling and bounded 429/5xx exponential backoff are enforced.
- Grounded JSON prompts, verbatim citation checks, per-claim lexical support,
  unsupported-claim stripping and dev-calibrated abstention share the serving
  and evaluation contracts. JSON/SSE expose `claims`, `included` flags and
  `answered_version`. Output is buffered until verification is complete.
- Serving defaults to extractive; opt in with `RAG_GENERATION_BACKEND=deepseek-flash`.
  Its frozen calibration is `configs/phase6_calibration.json`. Serving never reads
  `.cache/phase6/`. PostgreSQL rechecks current public ACLs at the external boundary.
- `bash scripts/phase6_eval.sh` completed in 264.84s with 167 successful provider
  calls. Eight ACL-denied restricted-collection cases (5 dev, 3 test) abstained
  locally without calls. Database/GPU artifacts were read only and preserved.
- Rescored using the successful cache after numeric-token boundary and delivered-
  claim metric corrections: 22.53s, 167 cache hits, **0 new provider calls**.
  Both executions are recorded in `results/phase6_results.json`.
- Frozen `data/eval/phase6_subset.json` contains 60 stratified test IDs, all 12
  unanswerable/version-unavailable test rows, all question types and both existing
  human-reviewed test rows. All 115 dev rows calibrate separate thresholds;
  the selected threshold for both generators is 0.0. Test does not tune decisions.
- Test correctness proxies: extractive 0.2833, extractive-verified 0.3167,
  llm-unverified 0.6167, llm-verified 0.5167. Verification reduces LLM coverage
  from 39 to 31 answers; its conditional lexical support is enforced by construction.
  No wrong-version answers occurred under explicit requested-version scoping.
- Dev selects verified DeepSeek over verified extractive under the recorded
  quality rule (correctness proxy 0.4087 vs 0.2261). Total token-cost estimate is
  $0.069812–$0.139625, not observed billing or a free-tier claim. The four historical
  human-reviewed gold rows are reported separately; no new human labels were collected.
- Deliverables: `results/phase6_results.json`, `results/phase6_table.md`,
  `docs/phase6_findings.md`; methodology explicitly labels lexical metrics as
  proxies rather than independent semantic correctness/faithfulness judgments.
- Verification: full offline suite **248 passed, 16 skipped**; `ruff check .`,
  full `mypy .` (113 source files), wrapper shell syntax and `git diff --check`
  passed. Phase 6 changes remain uncommitted on `phase-6-generation`.

## Phase 7 lean security / study pre-audit — 2026-10-28

- Added strict HS256 JWT authentication with required `sub`, `iat`, and `exp`,
  validated optional `groups`, `roles`, and `scope`, a 32-byte minimum secret,
  and verified-claims-only principal/group derivation. Health remains public;
  query, stream, document mutation, and job routes are protected. Mutation and
  job routes require `admin`, `ingest`, or `ingestion` role/scope.
- Query-body `principal` and `groups` are ignored at the HTTP boundary, preventing
  identity spoofing while retaining ingestion ACL payloads for administrators.
  Unauthorized restricted queries return normal HTTP 200 `not found` responses;
  scope versions, candidate traces, matches, citations, claims, and SSE metadata
  are derived only from authorized active evidence.
- Hardened memory/Postgres parent expansion, explicit-version scope reporting,
  public-provider boundary checks, and the in-memory ingestion cache so ACL
  grants/revocations and version deletion take effect immediately.
- Added configurable body/query/document/section/metadata limits, sliding-window
  principal/IP rate limiting with `Retry-After`, API request timeouts, and
  PostgreSQL connection plus statement timeouts.
- Added deterministic prompt-injection sanitization for query/passage/section/
  metadata values and verification guards for instruction-shaped claims, fake
  citation identities, and cross-version citations. The local benchmark covers
  six attacks across extractive and deterministic unverified-LLM outputs.
- Added Hypothesis properties for authorization soundness, group monotonicity,
  ACL revocation, and version deletion for the memory adapter and provisioned
  Postgres adapter path. The live closeout suite ran the Postgres paths against
  `evidence_rag_eval`; only the destructive migration-reset test is limited to a
  disposable database.
- `bash scripts/phase7_eval.sh` completed at $0 API cost. Prompt benchmark:
  deterministic-LLM attack success **1.000 → 0.000**, claim survival **1.000 →
  0.000**, citation-spoof survival **0.667 → 0.000**; extractive citation-spoof
  survival **0.333 → 0.000**.
- Study A created an isolated schema with enabled/forced RLS and a `NOBYPASSRLS`
  role under `SET LOCAL ROLE`, comparing p50/p95 with application ACL SQL. It
  measured zero ACL leakage for `alice`, `bob`+`sre`, and `mallory`. Study B used
  pgvector 0.8.7 HNSW with `ef_search=40`, a selective `pg-17` + `Functions and
  Operators` filter covering **383/20,756 (1.84%)** rows, and out-of-scope query
  vectors; HNSW was confirmed in the plan and both iterative modes reached
  recall@10 1.000 against exact ground truth.
- The initial no-listener result was caused by Docker being off; once the existing
  PostgreSQL environment was accessible, both studies were rerun against the
  configured database. The public corpus was reset by the intentionally destructive
  migration test before that test was guarded; Study B therefore used the preserved
  Phase 4 snapshot plus Phase 5 baseline vector artifact in the same database. No
  provider calls or paid API calls were made.
- Fixed the three audit findings: RLS/App leakage now render numeric zero counts;
  Study B uses an explicit <10% selective filter and `ef_search=40`; and live
  Postgres integration/Hypothesis paths execute through the configured eval DB
  without allowing the destructive reset test to touch it.
- Deliverables: `results/phase7_results.json`, `results/phase7_table.md`,
  `docs/phase7_findings.md`, `scripts/phase7_eval.py`, and
  `scripts/phase7_eval.sh`.
- Verification: live database suite **281 passed, 1 skipped**; `ruff check .`,
  full `mypy .` (119 source files), `git diff --check`, and the Phase 7 wrapper
  completed.

## Phase 8 packaging and protected-state closeout — 2026-10-29

- The recovered databases were frozen before Phase 8. A read-only canonical
  manifest records counts, columns, primary keys, and SHA-256 hashes for every
  table in `evidence_rag_eval`, `evidence_rag_recovery_20261028`, the preserved
  `public_pre_recovery_20261029` schema, and the surviving Phase 4/5 schemas.
  The before/after comparison matched every protected table exactly.
- A logical dump was attempted before edits but could not run: the installed
  `pg_dump` is PostgreSQL **15.19**, while the server is PostgreSQL **17.11**;
  no compatible PostgreSQL 17 client was present. The manifest is change
  detection only and is not claimed to be equivalent to `pg_dump`.
- Moved the disposable database fixture to `tests/conftest.py`. It now accepts
  only `RAG_TEST_ADMIN_DATABASE_URL`, creates a fresh `rag_test_<uuid>` database,
  owns the generated URL/name variables, and requires exact URL/name equality
  in every Postgres test helper. CI now passes the maintenance URL separately.
- Added trace generation metadata, cost/latency persistence, trace inspection,
  trace summary, corpus coverage, query generation modes, and sparse-vs-hybrid
  search selection. The Streamlit UI is under `src/rag_service/ui/`.
- Added the isolated `evidence_rag_demo` database and deterministic seed:
  **2 documents, 3 versions, 7 chunks, 7 chunk links, 6 hash embeddings, and
  4 ACL rows**. Compose uses a dedicated `evidence_rag_demo_pgdata` volume.
  The seed refuses to overwrite an existing schema.
- Added `scripts/phase8_eval.sh`. It created and dropped
  `rag_test_phase8_285bedad1f3645b985cc6b6c94182ebf`, measured 24 documents / 48
  chunks, ingestion p50/p95 **174.500/178.326 ms**, read-only query p50/p95
  **27.367/28.967 ms**, and API cost **$0.00**. Artifacts are
  `results/phase8_results.json`, `results/phase8_table.md`, and
  `docs/phase8_findings.md`.
- Safe full verification used explicit `hash-v1` and `token-overlap` adapters:
  **288 passed**, with a fresh disposable database created and dropped. No
  transformer weight initialization appeared in that run. An earlier default
  suite invocation did initialize local transformer weights; it was not used as
  the final safety result and no model encoding was run for recovery or Phase 8.
- Ruff, mypy, targeted observability tests, shell syntax, and the protected
  manifest comparison passed. Docker is unavailable in this environment, so
  Compose startup and browser UI smoke testing remain host checks.

## Full application corpus rebuild — 2026-10-29

- Created the isolated application database
  `evidence_rag_full_app_5d34bd5a2530` from the full three-version corpus. The
  protected source databases were not mutation targets.
- Applied current application migrations only to the new target.
- Confirmed the target baseline matched the source before vector work:
  32,719 active chunks, 20,756 BGE-small links, and 9,083 384-dimensional
  vectors.
- Inventoried 11,963 missing active links and 6,065 genuinely missing unique
  content hashes. No missing hash had a reusable vector row.
- Encoded the 6,065 unique texts with `BAAI/bge-small-en-v1.5` on CPU using
  the compatible configuration: 384 dimensions, normalized vectors, query
  instruction enabled, metadata prefix disabled. Inserted 6,065 vectors and
  11,963 links in six idempotent batches.
- Final target coverage is complete for the active corpus: 32,719 active
  chunks, 32,719 valid BGE-small links, and 15,148 vector records, all with
  384 dimensions.
- Full-corpus smoke query passed with live BGE-small CPU question encoding,
  PostgreSQL hybrid retrieval, explicit `pg-17` filtering, five matches,
  citations, and no abstention. DeepSeek was intentionally not called in the
  smoke test.
- Protected-state verification after the rebuild checked 52 tables and found
  zero count or canonical SHA-256 mismatches.
- Remaining runtime wiring: point the final application at the new target, set
  BGE-small instead of the hash demo encoder, and enable DeepSeek Flash after
  `DEEPSEEK_API_KEY` is configured locally. No phase 0–8 rebuild is required.

### Things I am unsure about

- The benchmark is a local single-process timing result, not a production
  capacity estimate.
- The recovered ACL rows are provenance from surviving Phase 4 artifacts, not
  proof of the lost database's complete historical ACL state.
- Demo hash vectors prove deterministic plumbing, not semantic embedding quality.

## Final application runtime verification — 2026-10-30

- Verified a non-empty local `DEEPSEEK_API_KEY` without printing its value. A
  direct `deepseek-flash` streaming preflight returned HTTP 200 and completed
  before final containers were started.
- Split the demo configuration into `.env.demo` and `docker-compose.demo.yml`.
  Updated `scripts/demo_up.sh` so demo commands always use those files and never
  source or overwrite the final `.env`.
- Final Compose wiring uses only `api`, `worker`, and `ui`, attaches to the
  existing `evidence-rag_default` network, and connects to the existing
  `evidence-rag-postgres-1` container and `evidence_rag_full_app_5d34bd5a2530`.
  The protected PostgreSQL container and volume remained running and unchanged.
- Host model-cache verification passed offline for
  `BAAI/bge-small-en-v1.5` (384 dimensions, unit-normalized) and
  `cross-encoder/ms-marco-MiniLM-L6-v2`. The cache is mounted read-only into
  `api` and `worker`; explicit `/hub` cache variables are required by the
  container library.
- Final API health passed on port 18010 and Streamlit UI reachability passed on
  port 18511. The API reported 32,719 public manual chunks.
- Added the target-only ACL fixture
  `postgresql-sre-operations-policy` with 3 private BGE-small vectors and
  groups `sre`/`docs-admins`. The public manual remained 32,719 chunks across
  three public versions; manual pre/post fingerprints matched.
 - Re-ran all six legacy DeepSeek acceptance cases through the canonical API.
   PG16 required one retry to obtain a supported verified answer. The final
   traces all returned HTTP 200 with expected version/citation/support behavior.
- ACL allow for `bob`/`sre` retrieved the private fixture locally. ACL deny for
  `alice` returned `not found` with zero matches and zero citations; the trace
  shows a local abstention and no provider metadata/call.
- The canonical Dockerfile build succeeded for all three final services after
  resilient pip settings and dependency/source layer separation. Obsolete
  local `:patched` image tags were removed. The canonical UI AppTest rendered an
  extractive live query with answer, version, citations, claim support, stage
  latency, and cost ledger; AppTest exceptions/errors were zero.
 - All DeepSeek traces now persist model, token usage, provider latency, attempt
   count, and positive public-rate cost estimates. The six final acceptance
   costs are `$0.00059452`, `$0.00060218`, `$0.00058102`, `$0.00053888`,
   `$0.00064942`, and `$0.00049728`; the existing unanswerable and repeat
   verification traces remain `$0.00060240` and `$0.00074341`.
 - Complete token counts, cache hits/misses, trace IDs, and costs are recorded
   in `results/final_runtime_acceptance_20261030.md`. Account billing is not
   observable.
- No database, protected volume, merge, or push was performed.
