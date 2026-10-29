# Full application corpus rebuild

## Purpose

Build the final application dataset from the complete three-version PostgreSQL
manual corpus, fill the missing BGE-small dense-vector coverage, and wire the
application to BGE-small retrieval plus the DeepSeek Flash answer generator.

This is an isolated application build. The source databases remain read-only and
are never used as mutation targets.

## Safety boundary

- Source databases: `evidence_rag_eval` and
  `evidence_rag_recovery_20261028`.
- Source connection policy: `default_transaction_read_only=on`.
- Target database: `evidence_rag_full_app_5d34bd5a2530`.
- Target status at start: did not exist.
- No source table, source schema, source volume, or existing volume may be
  deleted, truncated, migrated, or overwritten.
- Fine-tuned embedding models are excluded from this rebuild.

## Starting baseline

| Item | Count/value |
|---|---:|
| Documents | 1 |
| Document versions | 3 |
| Sections | 23,946 |
| Active chunks | 32,719 |
| BGE-small embedding records | 9,083 |
| BGE-small linked chunks | 20,756 |
| Active chunks without vector links | 11,963 |
| Vector dimensions | 384 |
| Embedder ID | `bge-small-en-v1.5` |

## Planned phases

1. Create the isolated target from the source without changing the source.
2. Verify target counts, schema, migrations, and source/target baseline hashes.
3. Inventory missing vector links and reusable content-hash vectors.
4. Reuse compatible vectors first; encode only genuinely missing unique texts with
   `BAAI/bge-small-en-v1.5` on CPU in resumable batches.
5. Validate dimensions, normalization, links, counts, and HNSW readiness.
6. Configure the final application for BGE-small retrieval and DeepSeek Flash.
7. Run full-corpus retrieval, ACL/version, API, and answer-verification checks.
8. Record final results, timings, resource use, and remaining limitations.

## Current status

- Preflight completed.
- Both source databases matched the baseline counts and embedder groups.
- Target `evidence_rag_full_app_5d34bd5a2530` created from the source template.
- Target counts and embedder groups match `evidence_rag_eval` exactly.
- No source or existing database was modified.
- Current migrations applied to the new target only.
- Inventory: 11,963 active chunks lack links, with 6,065 unique content hashes
  requiring encoding and zero reusable vectors among those missing links.
- Compatibility confirmed: `bge-small-en-v1.5`, 384 dimensions, normalized
  vectors, query instruction enabled, metadata prefix disabled.
- Timing batch: 64 texts encoded in 12.3s after a 6.0s model load; no writes.
- Batch 1: 1,024 vectors inserted, 1,981 links inserted, 187.7s encoding,
  5,041 unique hashes remaining.
- Batch 2: 1,024 vectors inserted, 2,058 links inserted, 194.8s encoding,
  4,017 unique hashes remaining.
- Batch 3: 1,024 vectors inserted, 1,995 links inserted, 197.2s encoding,
  2,993 unique hashes remaining.
- Batch 4: 1,024 vectors inserted, 2,015 links inserted, 211.4s encoding,
  1,969 unique hashes remaining.
- Batch 5: 1,024 vectors inserted, 2,024 links inserted, 208.6s encoding,
  945 unique hashes remaining.
- Final batch: 945 vectors inserted, 1,890 links inserted, 177.5s encoding,
  0 unique hashes remaining.
- Final target coverage: 32,719 active chunks, 32,719 valid BGE-small links,
  15,148 BGE-small vector records, all 384-dimensional.
- Protected verification after rebuild: 52 tables checked, 0 count mismatches,
  0 canonical SHA-256 mismatches.
- Full-corpus smoke passed with BGE-small CPU query encoding, PostgreSQL hybrid
  retrieval, `pg-17` filtering, 5 returned matches, citations, and no
  abstention. DeepSeek was intentionally not called during this smoke test.
- Next action: configure the final application runtime against the new target
  and enable DeepSeek Flash only if its local API key is available.

## Decision rule

If existing BGE-small vector configuration cannot be proven compatible with the
newly encoded vectors, the rebuild will use a separate embedder ID and re-embed
all unique corpus hashes rather than mixing incompatible vectors.
