# Question drafting rules

The NVIDIA API is dropped. Draft questions directly with the session model;
do not call an external model/API or read `.env`. Do not use a script, template,
or generator to produce questions. Read each passage and write each question.
Do not inspect retrieval results or retrieval code while drafting.

## Source selection

- Use dev and test lineages only, never blind or train. Spread sources across
  pg-15, pg-16, and pg-17.
- Read passages about 300–1500 characters long; skip near-empty, navigation,
  and entity-only sections.
- For factoid, exact-identifier, table, multi-hop, and ACL questions, prefer
  lineages with identical text in every version where they exist and absent
  from the diff miner's changed list. Set `version_independent=true` for these.
  If a changed lineage must be used, name the PostgreSQL version in the question
  and set `version_independent=false`.
- Factoid and identifier: sections defining a parameter, function, or setting.
- Table: table chunks. Multi-hop: two related sections of the same version.
- ACL: restricted sections specified in `data/acl_demo.yaml`.

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
- At a context-limit stopping point, commit and push, and record exactly which
  batches are complete and what remains in `docs/status.md`.
