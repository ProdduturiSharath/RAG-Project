# Phase 3 data card

The benchmark source is the official PostgreSQL documentation source, rather
than a page crawler. Each source archive contains `doc/src/sgml`, which is
parsed locally into `data/eval/source_sections.jsonl`. The raw archives and
extracted source are ignored by Git (`data/raw/` and `data/processed/`) and
must not be committed.

## Provenance

Retrieval date: **2026-10-04 UTC**

| Indexed version | Official source URL | License | SHA-256 of source archive |
| --- | --- | --- | --- |
| pg-15 (15.19) | https://ftp.postgresql.org/pub/source/v15.19/postgresql-15.19.tar.gz | PostgreSQL Documentation License (BSD-style; legal notice) | `4bf5474f0ee4afc55de5e71fb5cc8cd133ee56cd1bf16092093897b7c93328fb` |
| pg-16 (16.15) | https://ftp.postgresql.org/pub/source/v16.15/postgresql-16.15.tar.gz | PostgreSQL Documentation License (BSD-style; legal notice) | `4f200ca23dfb120ff9838f13ce06014aad1d3c432d16ee9f93ab2000c0eeef7b` |
| pg-17 (17.11) | https://ftp.postgresql.org/pub/source/v17.11/postgresql-17.11.tar.gz | PostgreSQL Documentation License (BSD-style; legal notice) | `5367f6fb2ec97efe1eb2e0c7926bb33438e51b0bd3a9733b88498056a7dc9a7e` |

The license was verified in the official legal notices:

- https://www.postgresql.org/docs/15/legalnotice.html
- https://www.postgresql.org/docs/16/legalnotice.html
- https://www.postgresql.org/docs/17/legalnotice.html

Those notices grant permission to use, copy, modify, and distribute the
documentation without fee, subject to retaining the copyright and notice. The
fetch script also verifies the published `.sha256` sidecar values before
extracting an archive:

```bash
python scripts/fetch_postgres_docs.py
PYTHONPATH=src python scripts/process_postgres_docs.py
PYTHONPATH=src python scripts/corpus_metrics.py
# Set RAG_EVAL_DATABASE_URL to an evidence_rag_eval or evidence_rag_dev database.
PYTHONPATH=src python scripts/ingest_postgres_docs.py
PYTHONPATH=src python scripts/build_benchmark.py
PYTHONPATH=src python scripts/validate_dataset.py
```

The evaluation database must be created separately from the disposable test
database (for a local Compose server, create `evidence_rag_eval` once with
`createdb -h 127.0.0.1 -U postgres evidence_rag_eval`). The ingestion command
prefers the full ignored extraction under `data/processed/postgresql`; the
committed source artifact is intentionally a compact evidence/owner-labeling
view rather than the downloaded corpus.

## Artifacts

- `eval/source_sections.jsonl`: generated evidence text and source locations.
- `eval/schema.json`: JSON Schema for one question record.
- `eval/splits.json`: one persisted assignment per stable section lineage,
  including the owner-only blind pool.
- `eval/diffs.jsonl`: adjacent-version changes and both-side evidence quotes.
- `eval/candidates.jsonl`: programmatic candidates; all have
  `author=generated` and `validated=false` until reviewed.
- `eval/benchmark_stats.json`: source, split, diff, and candidate counts.
- `acl_demo.yaml`: simulated principals/groups and restricted section seed.

Generated candidates are restricted to dev and test lineages. The dataset
builder never uses blind lineages; `scripts/label_dataset.py write` is the
owner's CLI-only path for authoring blind questions.
