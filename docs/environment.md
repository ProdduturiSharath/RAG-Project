# Environment and provider record

Last reviewed: 2026-10-02 (UTC, from the session environment).

## Answers from the project owner

| Question | Recorded answer | Source |
| --- | --- | --- |
| LLM provider | Google Gemini through Google AI Studio's OpenAI-compatible endpoint | Owner answer in Phase 0 session |
| Fixed model | Provisional choice: `gemini-2.5-flash-lite`; exact current free-tier availability must be revalidated before Phase 6 | Owner requested an exact current Flash/Flash-Lite model; Google AI docs returned HTTP 429 during this audit |
| Key availability | No key yet. The owner will create one in Google AI Studio before Phase 6. No key is committed. | Owner answer in Phase 0 session |
| Budget | `$0` paid spend. Free-tier Google AI Studio calls are allowed; stop and ask if free-tier limits block an experiment. | Owner answer in Phase 0 session |
| Embeddings/reranker | Local models only; no paid embedding API | Owner answer in Phase 0 session |
| Runtime OS | Ubuntu under WSL2; use `python3` and the repository `.venv` | Owner answer in Phase 0 session |
| Training environment | Google Colab free GPU for Phase 5 | Owner answer in Phase 0 session |
| Data policy | Only public documents may be sent to an external API | Owner answer in Phase 0 session |

## Provider verification

The intended Gemini OpenAI-compatible base URL is recorded as:

```text
https://generativelanguage.googleapis.com/v1beta/openai/
```

The intended request shape is the OpenAI chat-completions shape already used by
the adapter, with `temperature=0`. The official Google AI documentation URL is
<https://ai.google.dev/gemini-api/docs/openai>. Attempts to fetch that page on
2026-10-02 returned HTTP 429 from this environment. Therefore the endpoint,
free-tier status, limits, and the provisional model above are **not yet verified
for this run**. Revalidate from the official Google documentation and the
provider's model-list endpoint after the owner creates a key, before any Phase 6
experiment. Do not treat the provisional name as a measured or guaranteed
availability claim.

The official Google-maintained Gen AI SDK documentation was reachable at
<https://raw.githubusercontent.com/googleapis/python-genai/main/README.md> and
demonstrates current model aliases such as `gemini-flash-latest`; it is not used
as proof of AI Studio free-tier limits or a fixed model choice. Model license,
price, rate limits, and context/output limits remain an explicit Phase 6
verification item.

## Operational constraints

- Keep `GEMINI_API_KEY` out of source control and `.env.example` values.
- API calls are not made in CI.
- Later evaluation-only LLM/API-embedding calls must be cached under `.cache/`
  by model and prompt hash; errors are never cached and cost is recorded.
- Add request throttling and exponential-backoff handling before enabling the
  provider adapter for an experiment.
- The serving API must not use the evaluation cache.

## Local toolchain

The environment initially lacked `python3-venv` and pip. A no-`ensurepip`
virtual environment was created and pip was bootstrapped from
<https://bootstrap.pypa.io/get-pip.py>. The exact installed versions are
recorded by `docs/status.md` and the pinned lock file.
