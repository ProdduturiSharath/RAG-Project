# Phase 3 corpus benchmark dataset card

Status: final gold built on `phase-3-corpus-benchmark` (2026-10-10 UTC).

## Sources

The corpus is the official PostgreSQL documentation source for PostgreSQL
15.19, 16.15, and 17.11, parsed from the `doc/src/sgml` trees. The committed
evaluation source artifact is `data/eval/source_sections.jsonl`; the full local
source corpus is not required for the committed validation path. Version
alignment, section lineage, tables, code, headings, and captions are retained
in the source records.

## Question construction

The questions were written directly from corpus passages by the drafting
session. Version-specific questions were grounded in real adjacent-version
diffs, including changed defaults, added or removed parameters, renamed
settings, and changed table rows. Multi-hop questions require their two
recorded evidence spans. ACL questions use the simulated policy in
`data/acl_demo.yaml`. Unanswerable and version-unavailable questions use
identifier absence checks rather than invented answers.

## Validation and review

Automated construction and validation check verbatim evidence quotes, persisted
split membership, version metadata, identifier absence, paraphrase parameter
leaks, multi-hop structure, ACL policy, and duplicate questions. An independent
session audited all 222 candidates using only each question, answer, and
evidence; it rejected **10 of 222** and flagged none. The six rows in
`data/eval/reviewed.jsonl` are the only historical human reviews. Two reviewed
rows had parser-repaired evidence quotes, so they fell back to the independent
audit: one remains in gold as `model_audit`, and the rejected
`draft-257b83c46f868ef6` stays out. Thus four gold rows retain
`review_method=human`.

Final gold is `data/eval/gold.jsonl`. Every row has
`review_status=accepted`, `validated=true`, and one of `human`, `model_audit`,
or `owner_written` as `review_method`.

## Final gold composition

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

## Version-independent evidence

`gold_versions` lists the PostgreSQL versions whose source record is exactly
equivalent for a version-independent question. The validator computes the
intersection across all evidence spans and checks every recorded list. A
version-specific question instead names its target PostgreSQL version and uses
evidence from that version; its `gold_versions` list is empty.

## Repaired table representation

This compact table chunk demonstrates that the section title and heading path
are intact while the table caption is stored separately:

```json
{
  "version": "pg-16",
  "kind": "table",
  "title": "pg_subscription",
  "section_path": ["System Catalogs", "pg_subscription"],
  "caption": "pg_subscription Columns",
  "table_rows": [
    ["Column Type Description"],
    ["substream char Controls how to handle the streaming of in-progress transactions: ..."],
    ["subconninfo text Connection string to the upstream database"]
  ]
}
```

## Limitations

- The same model family wrote and audited the questions, so their blind spots
  are shared.
- Human review was minimal and covered only the few rows in the existing
  review file; the independent audit is the validation decision for the rest.
- Version-specific questions come in pairs tied to real changes between
  adjacent PostgreSQL versions, so they are not an independent random sample
  of all documentation.
- The models may have seen the public PostgreSQL documentation during training.
- The owner-written blind set is pending and contributes no rows to this gold
  artifact.
