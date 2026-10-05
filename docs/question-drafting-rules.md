# Question drafting rules

The NVIDIA API is dropped. Draft questions directly with the session model;
do not call an external model/LLM API or read `.env`. Git and `gh` are allowed.
Do not use a script, template,
or generator to produce questions. Read each passage and write each question.
Do not inspect retrieval results or retrieval code while drafting.

## Source selection

- Use dev and test lineages only, never blind or train. Spread sources across
  pg-15, pg-16, and pg-17.
- Splits are section-family isolated: prose, all table/code blocks, and every
  version inherit one stable section identity (`metadata.section_lineage` for
  blocks), even without prose. Connected multi-hop families share one split.
  The approved one-time correction is recorded in `data/eval/split-migration.json`;
  subsequent refreshes preserve family assignments and blind **families**.
- Read passages about 300–1500 characters long; skip near-empty, navigation,
  and entity-only sections.
- For factoid, exact-identifier, table, multi-hop, and ACL questions, prefer
  lineages with identical text in every version where they exist and absent
  from the diff miner's changed list. Set `version_independent=true` for these.
  If a changed lineage must be used, name the PostgreSQL version in the question
  and set `version_independent=false`.
- Factoid and identifier: sections defining a parameter, function, or setting.
- Table: table chunks. Multi-hop: two related sections of the same version.
- Multi-hop must be one connected question whose answer requires both passages,
  with the second fact depending on the first; never independent questions
  joined by “and”. Store a short `reasoning_chain` for review.
- ACL: restricted sections specified in `data/acl_demo.yaml`.
- Include allowed requesters as well as denied ones: add up to four allowed
  cases when the existing pool is all denied, and report both counts.
- Every `version_independent=true` row stores its primary `lineage_key` and
  `gold_versions`, computed by comparing full evidence-source text across
  versions. Multi-hop rows use the intersection for both sources; each evidence
  span also stores its own gold versions. This is bookkeeping, not generation.

## Question and evidence requirements

- Targets: factoid 35, exact-identifier 35, table 25, multi-hop 12,
  unanswerable 18, ACL 8. Produce fewer if sources are scarce.
- Write specific, natural user questions answerable from the supplied text
  alone, with short factual answers. No filler or numbered variants.
- Never refer to “according to the passage/text/section”, “this section”,
  or otherwise ask about “the passage/text/section”.
- For about half of factoid and identifier questions, describe behavior rather
  than naming the parameter; set `paraphrased=true` for those questions.
- Copy `evidence_quote` character for character from source text; multi-hop
  requires two quotes, one for each source section.
- Unanswerable questions ask about a plausible PostgreSQL feature/parameter
  that does not exist, or a real parameter in a version without it. Use answer
  `Not answerable` and an empty `evidence_quote`. Invented identifiers must be
  absent from the entire corpus.

## Diff questions and workflow

- Targets: up to 50 answer-changing version-specific, 25 unchanged controls,
  10 version-unavailable. Use real default, parameter add/remove/rename, or
  table-row diffs only, never “other text changes”. Report target shortfalls.
- Expected answers and evidence must come from the diff/source.
- Write batches of about 25 in one file write to
  `data/eval/drafts/batch_NNN.json`, import, fix/drop failures, and commit.
  Push every three batches. Never mark a draft `validated=true`.
- Imported rows use `author=llm_drafted`, `drafted_by=omnirush/gpt-6-astra`,
  `paraphrased`, `version_independent`, and `validated=false`.
- Human rejection records `review_status=rejected, validated=false`; acceptance
  records `review_status=accepted, validated=true`. Final-gold eligibility
  requires both validated true and explicit accepted status, including legacy
  records. Future owner-authored blind rows also record explicit acceptance.
- At a context-limit stopping point, commit and push, and record exactly which
  batches are complete and what remains in `docs/status.md`.
- Complete the remaining batches in this session. Show samples/report only at
  the end; an earlier stop is allowed only past the 85% context checkpoint.
- Check PR #4 CI with `gh` after pushing; do not merge it or start Phase 4.
