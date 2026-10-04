# Phase 3 report: corpus and benchmark

Date: 2026-10-04 UTC
Branch: `phase-3-corpus-benchmark`

## 1. Implemented

- Added `scripts/fetch_postgres_docs.py`, which politely downloads the official
  PostgreSQL 15.19, 16.15, and 17.11 source archives with a user agent,
  verifies the published SHA-256 sidecars, and extracts only `doc/src/sgml`.
- Added the SGML parser in `src/rag_service/benchmark/corpus.py`. It retains
  stable section IDs, lineage keys, prose, tables, code, source file, and source
  line. Raw archives and extracted trees remain ignored.
- Added `scripts/ingest_postgres_docs.py` for all three versions through the
  existing Postgres ingestion pipeline with `bge-small-en-v1.5`. It rejects
  test databases and requires a database name containing `eval` or `dev`.
  `scripts/corpus_metrics.py` records parser/chunker counts independently of
  model/database availability.
- Added persisted lineage splits in `data/eval/splits.json` with train, dev,
  test, and blind assignments. The builder never uses blind lineages.
- Added `src/rag_service/benchmark/diffs.py` and `data/eval/diffs.jsonl` for
  adjacent-version section alignment, default changes, parameter additions,
  removals and renames, table-row changes, and both-side evidence.
- Added deterministic candidate generation, the JSON Schema, validation, and
  the CLI-only labeling tool (`scripts/label_dataset.py`).
- Added `data/acl_demo.yaml` with simulated principals/groups and restricted
  section titles.
- Added a CI validator step and focused unit tests in
  `tests/unit/test_benchmark.py`.
- SciFact and BEIR were not added; they remain Phase 4 work.

## 2. Corpus and ingestion metrics

The source artifact was generated from the official archives and contains the
following structural counts. Chunk counts use the committed configuration of
220 maximum tokens and 35 overlap tokens and are produced by
`scripts/corpus_metrics.py`.

| Version | Documents | Sections | Chunks | Table chunks | Code chunks |
| --- | ---: | ---: | ---: | ---: | ---: |
| pg-15 | 1 | 7,332 | 10,013 | 13 | 3,708 |
| pg-16 | 1 | 7,417 | 10,144 | 14 | 3,760 |
| pg-17 | 1 | 7,504 | 10,263 | 14 | 3,824 |

The bge-small Postgres load command is implemented but could not execute in
this WSL session: Docker is unavailable and no Postgres server is listening on
`127.0.0.1:5432`. The attempted command failed at migration with connection
refused, so no embedding time is fabricated. `corpus_metrics.json` records
`embedding_seconds: null`; after provisioning `evidence_rag_eval`, run:

```bash
RAG_EVAL_DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval \
  PYTHONPATH=src python scripts/ingest_postgres_docs.py
```

That command writes per-version embedding time and total embedding time to
`data/eval/ingestion_metrics.json` and ingests `pg-15`, `pg-16`, and `pg-17`
separately while reusing the stable lineage keys.

## 3. Diff miner

The full extracted source contained 11,909 unique lineages. Adjacent-version
matching found 10,344 lineage/version matches and 599 changed lineages. The
599 diff records contain:

| Change kind | Count |
| --- | ---: |
| Changed defaults | 15 |
| Parameters added | 122 |
| Parameters removed | 51 |
| Parameters renamed | 5 |
| Table rows added | 3 |
| Table rows removed | 3 |
| Other text changes | 521 |

The miner writes both the old and new evidence quote with its explicit version
to `data/eval/diffs.jsonl`.

## 4. Splits and candidates

| Split | Lineages |
| --- | ---: |
| train | 3,565 |
| dev | 3,557 |
| test | 3,572 |
| blind | 1,215 |

The generated pool contains exactly 198 dev/test candidates:

| Type | Count |
| --- | ---: |
| factoid | 30 |
| exact-identifier | 40 |
| table | 20 |
| multi-hop | 10 |
| version-specific answer-changing | 40 |
| unchanged control | 20 |
| version-unavailable | 8 |
| unanswerable | 15 |
| ACL | 15 |

All generated rows have `author=generated` and `validated=false`. Blind
lineages have no generated questions. The labeling tool's `write` mode shows
one persisted blind section at a time, accepts a typed question, and requires
an exact evidence span from the displayed text.

## 5. Five generated samples

1. **Factoid, pg-15** — “What does the PostgreSQL documentation state in the
   section Acronyms?”  Evidence: “Acronyms\nThis is a list of acronyms
   commonly used in the PostgreSQL documentation and in discussions about
   PostgreSQL .”
2. **Exact identifier, pg-15** — “Which exact identifier is named in the
   section Acronyms?”  Evidence: “pg_lsn”.
3. **Table, pg-15** — “What row is listed for LC_CTYPE in the Overview table in
   pg-15?”  Evidence: “| LC_CTYPE | Character classification (What is a letter? Its
   upper-case equivalent?) |”.
4. **Version-specific, pg-16** — “What changed in the section text text in
   pg-16? [variant 135]”  Evidence: “gcc -fPIC -c foo.c\ngcc -shared -o
   foo.so foo.o”. The answer is
   version-scoped to the pg-16 side of the mined change.
5. **ACL, pg-15** — “What does the restricted section Client Authentication
   say?”  Evidence: “Client Authentication\nWhen a client application connects
   to the database server, it specifies which PostgreSQL database user name it
   wants to connect as, much the same way one logs into a Unix computer as a
   particular user.”

## 6. Validator output

Command:

```bash
PYTHONPATH=src python scripts/validate_dataset.py
```

Output:

```json
{
  "blind_lineages": 1215,
  "counts_dev_test": {
    "acl": 15,
    "exact_identifier": 40,
    "factoid": 30,
    "multi_hop": 10,
    "table": 20,
    "unanswerable": 15,
    "unchanged_control": 20,
    "version_specific": 40,
    "version_unavailable": 8
  },
  "errors": [],
  "lineages": 11909,
  "records": 198,
  "source_records": 1351,
  "valid": true
}
```

The validator checks required schema fields and types, exact evidence presence
in the stated source version, duplicate questions, persisted split membership,
blind exclusion, and target type balance. The unit test explicitly makes a
lineage appear in two persisted split lists and verifies that validation fails.

## 7. Verification and remaining environment work

- Official archive checksums and the PostgreSQL documentation license are
  recorded in `data/README.md` and `data/source-manifest.json`.
- `ruff check src tests scripts` passed.
- `mypy src tests` passed.
- `tests/unit/test_benchmark.py` passed: 4 tests.
- The full test suite was run once after this report was added: `31 passed,
  16 skipped`.
- The only remaining Phase 3 operation is the real bge-small database load and
  its measured embedding-time artifact, blocked here solely by the unavailable
  Postgres service. No SciFact/BEIR work was started.

## Things I am unsure about

- PostgreSQL SGML contains presentation-only tables and unresolved cross-file
  entities. Empty presentation tables are excluded; unresolved entity text is
  retained so evidence remains faithful to the source parser output.
- The generated version-specific pool includes genuine text changes in
  addition to specialized parameter/default/table changes; human review should
  prefer the specialized records when labeling final evaluation questions.

## Abstractions or code that should be removed

No Phase 3 abstraction was identified for removal. The parser, diff miner,
dataset builder, validator, and CLI are separate because each has an offline
artifact and a focused testable responsibility.
