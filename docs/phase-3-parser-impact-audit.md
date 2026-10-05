# Bounded Phase 3 parser-impact audit

Scope: the **11 flagged candidates**, **six extra candidates**, and three
examples of table-title overwrite. Inspected the existing parsed records and
corresponding local SGML only. No parser/source changes, re-ingestion, embedding
work, model calls, or private blind questions. This is a bounded audit, not a
claim that every corpus record is lossless.

## Flagged evidence: all 11 answers remain supported

The missing labels in these particular evidence quotes are cross-references
for further reading, rather than facts required by the question. They are
cosmetic **for the existing answers**, although the corresponding larger
passages contain some meaningful omissions listed below.

| Candidate ID | Topic | Raw source / finding |
| --- | --- | --- |
| `draft-257b83c46f868ef6` | multixact member cache | PG17 `config.sgml:2046`: omitted `pgdata-contents-table` reference; `pg_multixact/members` retained. Human accepted. |
| `draft-2698580abdaeb4fb` | multixact offset default | PG17 `config.sgml:2065`: same omitted reference; 16 blocks and unit definition retained. Human accepted. |
| `draft-05e120c03871ce0e` | notify buffers restart | PG17 `config.sgml:2084`: reference missing; server-start-only rule retained. |
| `draft-59e8d98dc1e8267d` | serializable buffers default | PG17 `config.sgml:2103`: reference missing; default 32 retained. |
| `draft-9087662e522341da` | subtransaction buffer sizing | PG17 `config.sgml:2122`: reference missing; `shared_buffers/512` and 16–1024 bounds retained. |
| `draft-aa8fc2079022d8f2` | transaction cache setting | PG17 `config.sgml:2143`: reference missing; `transaction_buffers` and `pg_xact` retained. |
| `draft-29bf0d3d09985e6f` | GEQO/current_setting chain | PG15 `config.sgml:267`: admin-functions reference missing; function name, argument, and GEQO setting retained. |
| `draft-434bc40422c18e75` | disable JIT cost threshold | PG17 `config.sgml:6062`: general JIT reference missing; `-1` rule retained. |
| `draft-580cf5be88985635` | prepared generic-plan JIT | PG16 `jit.sgml:125`: PREPARE reference missing; prepare-time decision rule retained. |
| `draft-9c2802b2b594163e` | when to set inlining cost | PG17 `jit.sgml:125`: same reference loss; inlining setting is supplied by the other evidence passage. |
| `draft-54999895baea7983` | short-query JIT overhead | PG16 `config.sgml:5865`: general JIT reference missing; activation threshold and overhead explanation retained. |

## Small extra sample and meaningful gaps

Six extra candidates were inspected:

- `draft-229c3274e4f0153b` and `draft-0a0f7eeddc1dc6b4`: the two accepted
  `vacuum_buffer_usage_limit` defaults. SGML has **256 kB** (PG16
  `config.sgml:2028`) and **2MB** (PG17 `config.sgml:1974`), matching the quotes.
  The larger paragraph loses the command names in “overridden for and when”:
  the omitted xrefs are **VACUUM** and **ANALYZE**. This loses meaning, but not
  either reviewed default answer.
- `draft-d0c080d56602eee6` and `draft-5a6158db8b6f03ae`: accepted
  `pg_subscription.substream` types. PG15/PG16 `catalogs.sgml:7874/7922`
  explicitly retain **bool/char**. Their section title/path is overwritten by
  the table title “pg_subscription Columns”; factual types are unaffected.
- `draft-0c3e3fe9fd50f266`: the anti-wraparound autovacuum answer is intact.
  In the neighboring definition at PG16 `config.sgml:8457`, the omitted
  `guc-track-counts` reference erases the **track_counts** prerequisite, leaving
  “however, must also be enabled”. This is substantive condition loss.
- `draft-aaf9a56514c47f0f`: foreign-server connection changes still require
  reconnection, as quoted. In `postgres-fdw.sgml`, entry
  `guc-pgfdw-application-name`, omission of `guc-application-name` loses the
  target parameter name from its defining sentence. Its later explicit
  `application_name` mention makes this answer intact, but the definition is
  degraded.

Within the flagged JIT passages, omitted xrefs also erase **jit_above_cost**,
**jit_inline_above_cost**, **jit_optimize_above_cost**, **jit**, and **EXPLAIN**
from surrounding explanations (`jit.sgml`). These are meaningful losses of
referents, not merely formatting. The selected evidence for the three existing
multi-hop questions still contains the facts necessary for their answers.
Inline links that contain explicit text (SHOW, SET, and application_name)
retain that text; empty `xref` elements have no fallback rendering.

## Table-title overwrite: context and parent-path damage

`corpus.py` handles every `<title>` as the current section's title, even during
table capture. A later table title replaces the section title and its path.
Examples inspected in PG16:

| Stable section | Actual section title | Stored title | Effect |
| --- | --- | --- | --- |
| `monitoring-pg-stat-activity-view` | pg_stat_activity | Wait Events of Type Timeout | All 13 records get the last table's unrelated title; section context is materially wrong. |
| `runtime-config-wal-settings` | Settings | synchronous_commit Modes | Both prose/table records inherit a narrower table title; WAL setting context is mislabeled. |
| `catalog-pg-subscription` | pg_subscription | pg_subscription Columns | Both records inherit the table title; context remains recognizable but is still incorrect metadata. |

A read-only synthetic example confirmed that children encountered after a
table inherit the overwritten **parent path**. Explicit section IDs and block
`metadata.section_lineage` survive; this is why split isolation must use those
identities. Generated fallback IDs use parent-path text, so repairing title
handling can also affect those IDs and needs a separate impact plan.

ACL classification currently matches title/path strings. A synthetic
`Manual / Authentication` section becomes `Manual / Values` after a table
title, demonstrating loss of the restricted keyword and a possible
classification change. The three real examples above do **not** change their
current ACL classification: the Monitoring/Server Configuration ancestors
remain, and pg_subscription has no matching restricted ancestor. All current
ACL candidates retain a Server Configuration or Database Roles ancestor in
their saved evidence paths; this audit did not identify an allowance flip in
those candidates. It does not establish corpus-wide ACL metadata correctness.

## Six human reviews and recommendation

**All six accepted answers remain supported; none requires rejection or a
changed answer from this audit.** The two pg_subscription reviews should get a
metadata/context recheck after a parser repair because their section titles
are overwritten. The other four reviewed questions have intact parameter names
and numeric/cache facts; the two missing “see” references are cosmetic for their
answers. The review file and decisions were left unchanged.

Recommend a separately approved parser repair: keep table titles separate from
section title state, preserve parent identity explicitly, render xrefs using
target labels/parameter names, and retain semantic inline text. Before applying
it, compare fallback IDs, section/parent metadata, evidence offsets, and ACL
classification; then plan any corpus refresh separately. No repair, re-ingest,
or re-embed was performed in this cleanup.
