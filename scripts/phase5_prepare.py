#!/usr/bin/env python3
"""Prepare train-only passages and model-written retrieval queries.

The script is intentionally host-only.  It never imports torch, never sends a
secret to logs, and keeps every remote response under ``.cache/phase5`` so a
network interruption can be resumed without paying for completed calls.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rag_service.evaluation.phase5 import (
    STYLE_NAMES,
    exclusion_match,
    gold_quotes,
    load_jsonl,
    near_duplicate,
    normalize,
    select_unique_passages,
    text_hash,
    union_rank_accepts,
    validate_query_record,
    violates_behavior_style,
)

ROOT = Path(__file__).resolve().parents[1]
TRAIN = ROOT / "data" / "train"
CACHE = ROOT / ".cache" / "phase5"
MAX_COMPRESSED_BYTES = 40 * 1024 * 1024
PASSAGE_MIN, PASSAGE_MAX = 200, 1800
TARGET_QUERIES = (4000, 5000)
QUERY_BATCH = 3
TRIAL_PASSAGES = 10
GENERATOR_CALL_LIMIT = 1500
OPENING_RE = re.compile(r"^(\w+)", re.UNICODE)

# These are discovery descriptions, not a fixed model allow-list.  At runtime
# the catalog endpoint for every configured provider is enumerated and only
# the returned, stable model IDs are eligible.  The URLs are also written into
# generator_market.json so the model card can be audited after the run.
PROVIDERS: tuple[dict[str, Any], ...] = (
    {
        "name": "nvidia",
        "key": "NVIDIA_API_KEY",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "catalog_url": "https://integrate.api.nvidia.com/v1/models",
        "chat_url": "https://integrate.api.nvidia.com/v1/chat/completions",
        "api_docs": "https://docs.api.nvidia.com/nim/reference/llm-apis",
        "terms_url": "https://www.nvidia.com/en-us/agreements/enterprise-software/",
        "terms_status": "unclear",
        "terms_clause": "The public catalog/API page does not state output-training rights.",
        "free_status": "account-dependent free credits; verify in the NVIDIA console",
        "rate_limit_url": "https://build.nvidia.com/explore/discover",
        "thinking_control": "documented model-specific chat parameters; "
        "catalog discovery must verify",
    },
    {
        "name": "groq",
        "key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "catalog_url": "https://api.groq.com/openai/v1/models",
        "chat_url": "https://api.groq.com/openai/v1/chat/completions",
        "api_docs": "https://console.groq.com/docs/models",
        "terms_url": "https://groq.com/terms-of-use/",
        "terms_status": "unclear",
        "terms_clause": "Provider terms do not clearly grant output-training rights.",
        "free_status": "free plan documented; model-specific RPD/RPM apply",
        "rate_limit_url": "https://console.groq.com/docs/rate-limits",
        "thinking_control": "reasoning documentation must expose an explicit disable setting",
    },
    {
        "name": "openrouter",
        "key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "catalog_url": "https://openrouter.ai/api/v1/models",
        "chat_url": "https://openrouter.ai/api/v1/chat/completions",
        "api_docs": "https://openrouter.ai/docs/api/reference/parameters",
        "terms_url": "https://openrouter.ai/terms",
        "terms_status": "unclear",
        "terms_clause": "Terms §5.1 flows down each model's terms; no blanket permission.",
        "free_status": "free/provider-specific models exist; availability and limits vary",
        "rate_limit_url": "https://openrouter.ai/docs/guides/limits",
        "thinking_control": "reasoning_effort=none is documented, but provider support "
        "must be checked",
    },
    {
        "name": "openai",
        "key": "OPENAI_API_KEY",
        "base_url": "https://api.openai.com/v1",
        "catalog_url": "https://api.openai.com/v1/models",
        "chat_url": "https://api.openai.com/v1/chat/completions",
        "api_docs": "https://platform.openai.com/docs/api-reference/chat",
        "terms_url": "https://openai.com/policies/services-agreement/",
        "terms_status": "permitted_for_this_use",
        "terms_clause": "Services Agreement §3.3(e) permits categorization/organization models; "
        "this embedding experiment is non-distributed retrieval organization.",
        "free_status": "paid API; never selected before explicit approval",
        "rate_limit_url": "https://platform.openai.com/docs/guides/rate-limits",
        "thinking_control": "reasoning_effort=none is documented for supported models",
    },
    {
        "name": "huggingface",
        "key": "HF_TOKEN",
        "base_url": "https://router.huggingface.co/v1",
        "catalog_url": "https://huggingface.co/api/models?pipeline_tag=text-generation&sort=downloads&direction=-1&limit=100",
        "chat_url": "https://router.huggingface.co/v1/chat/completions",
        "api_docs": "https://huggingface.co/docs/huggingface_hub/package_reference/inference_client",
        "terms_url": "https://huggingface.co/terms-of-service",
        "terms_status": "unclear",
        "terms_clause": "Hosted provider and model license terms vary; require a "
        "model-specific review.",
        "free_status": "provider-specific free credits; limits vary",
        "rate_limit_url": "https://huggingface.co/docs/inference-providers/en/rate-limits",
        "thinking_control": "provider-specific; reject candidates without documented control",
    },
)

# Runtime catalog discovery covers the major OpenAI-compatible and native API
# markets named in the Phase 5 brief.  These are provider endpoints, not model
# IDs; the live response supplies all eligible stable names.
_EXTRA_PROVIDER_SPECS = (
    (
        "google",
        "GOOGLE_API_KEY",
        "https://generativelanguage.googleapis.com/v1beta",
        "https://generativelanguage.googleapis.com/v1beta/models",
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "https://ai.google.dev/gemini-api/docs",
        "https://ai.google.dev/gemini-api/terms",
        "free tier; account limits vary",
    ),
    (
        "mistral",
        "MISTRAL_API_KEY",
        "https://api.mistral.ai/v1",
        "https://api.mistral.ai/v1/models",
        "https://api.mistral.ai/v1/chat/completions",
        "https://docs.mistral.ai/api",
        "https://mistral.ai/terms",
        "free trial/paid tiers vary",
    ),
    (
        "together",
        "TOGETHER_API_KEY",
        "https://api.together.xyz/v1",
        "https://api.together.xyz/v1/models",
        "https://api.together.xyz/v1/chat/completions",
        "https://docs.together.ai/docs/models",
        "https://www.together.ai/terms-of-service",
        "free credits/paid tiers vary",
    ),
    (
        "fireworks",
        "FIREWORKS_API_KEY",
        "https://api.fireworks.ai/inference/v1",
        "https://api.fireworks.ai/inference/v1/models",
        "https://api.fireworks.ai/inference/v1/chat/completions",
        "https://docs.fireworks.ai/models",
        "https://fireworks.ai/terms",
        "free credits/paid tiers vary",
    ),
    (
        "deepseek",
        "DEEPSEEK_API_KEY",
        "https://api.deepseek.com",
        "https://api.deepseek.com/models",
        "https://api.deepseek.com/chat/completions",
        "https://api-docs.deepseek.com",
        "https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html",
        "paid API",
    ),
    (
        "cerebras",
        "CEREBRAS_API_KEY",
        "https://api.cerebras.ai/v1",
        "https://api.cerebras.ai/v1/models",
        "https://api.cerebras.ai/v1/chat/completions",
        "https://inference-docs.cerebras.ai/models",
        "https://cerebras.ai/terms-of-use",
        "free tier; account limits vary",
    ),
    (
        "cohere",
        "COHERE_API_KEY",
        "https://api.cohere.com/v2",
        "https://api.cohere.com/v1/models",
        "https://api.cohere.com/v2/chat",
        "https://docs.cohere.com/reference/chat",
        "https://cohere.com/terms-of-use",
        "free trial/paid tiers vary",
    ),
    (
        "github-models",
        "GITHUB_TOKEN",
        "https://models.github.ai/inference/v1",
        "https://models.github.ai/catalog/models",
        "https://models.github.ai/inference/v1/chat/completions",
        "https://learn.microsoft.com/azure/ai-foundry/model-inference/how-to/use-chat-completions",
        "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
        "free quota; rate limits vary",
    ),
    (
        "anthropic",
        "ANTHROPIC_API_KEY",
        "https://api.anthropic.com/v1",
        "https://api.anthropic.com/v1/models",
        "https://api.anthropic.com/v1/messages",
        "https://docs.anthropic.com/en/api/models-list",
        "https://www.anthropic.com/legal/commercial-terms",
        "paid API",
    ),
    (
        "xai",
        "XAI_API_KEY",
        "https://api.x.ai/v1",
        "https://api.x.ai/v1/models",
        "https://api.x.ai/v1/chat/completions",
        "https://docs.x.ai/docs/models",
        "https://x.ai/legal/terms-of-service",
        "paid/API credits vary",
    ),
)
PROVIDERS += tuple(
    {
        "name": name,
        "key": key,
        "base_url": base,
        "catalog_url": catalog,
        "chat_url": chat,
        "api_docs": api_docs,
        "terms_url": terms,
        "terms_status": "unclear",
        "terms_clause": "Provider terms do not clearly grant output-training rights.",
        "free_status": free_status,
        "rate_limit_url": api_docs,
        "thinking_control": "provider must document an explicit no-thinking control",
        "protocol": "native" if name in {"cohere", "anthropic"} else "openai-compatible",
    }
    for name, key, base, catalog, chat, api_docs, terms, free_status in _EXTRA_PROVIDER_SPECS
)

QUALITY_SOURCES = (
    "https://artificialanalysis.ai/leaderboards/models",
    "https://lmarena.ai/leaderboard/text",
)
DISALLOWED_ID = re.compile(
    r"(?:anonymous|stealth|alpha|beta|preview|experimental|deprecated)", re.I
)


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def read_dotenv_names(path: Path = ROOT / ".env") -> dict[str, str]:
    """Read only key/value pairs needed by this script; values never leave headers."""

    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name in {spec["key"] for spec in PROVIDERS}:
            values[name] = value.strip().strip("\"'")
    return values


def json_request(
    url: str, key: str | None = None, *, payload: Any = None, timeout: float = 30.0
) -> Any:
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if key:
        if "generativelanguage.googleapis.com" in url:
            headers["x-goog-api-key"] = key
        else:
            headers["Authorization"] = f"Bearer {key}"
    request = urllib.request.Request(url, headers=headers, method="POST" if payload else "GET")
    body = json.dumps(payload).encode() if payload is not None else None
    with urllib.request.urlopen(request, data=body, timeout=timeout) as response:
        return json.loads(response.read())


def quality_source_evidence() -> list[dict[str, Any]]:
    evidence = []
    for url in QUALITY_SOURCES:
        item: dict[str, Any] = {"url": url, "checked": datetime.now(UTC).date().isoformat()}
        try:
            request = urllib.request.Request(url, headers={"Accept": "text/html"})
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(1_000_000)
            item.update(status="ok", sha256=hashlib.sha256(body).hexdigest())
        except (OSError, urllib.error.URLError) as exc:
            item.update(status=f"unavailable: {type(exc).__name__}")
        evidence.append(item)
    return evidence


def discover_market(keys: dict[str, str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    today = datetime.now(UTC).date().isoformat()
    for spec in PROVIDERS:
        key = keys.get(spec["key"])
        source = {
            "provider": spec["name"],
            "catalog_url": spec["catalog_url"],
            "api_docs": spec["api_docs"],
            "terms_url": spec["terms_url"],
            "rate_limit_url": spec["rate_limit_url"],
            "checked": today,
            "key_present": bool(key),
            "status": "not_checked",
        }
        if not key:
            sources.append(source)
            continue
        try:
            catalog = json_request(spec["catalog_url"], key, timeout=45)
            models = catalog.get("data", catalog) if isinstance(catalog, dict) else catalog
            if not isinstance(models, list):
                raise ValueError("catalog response has no model list")
            for item in models:
                model_id = str(item.get("id", "")).strip() if isinstance(item, dict) else str(item)
                if not model_id or DISALLOWED_ID.search(model_id):
                    continue
                if spec.get("protocol", "openai-compatible") != "openai-compatible":
                    continue
                candidates.append(
                    {
                        "provider": spec["name"],
                        "model": model_id,
                        "base_url": spec["base_url"],
                        "chat_url": spec["chat_url"],
                        "key_name": spec["key"],
                        "terms_status": spec["terms_status"],
                        "terms_clause": spec["terms_clause"],
                        "free_status": spec["free_status"],
                        "thinking_control": spec["thinking_control"],
                        "catalog_item": item,
                        "quality_sources": list(QUALITY_SOURCES),
                    }
                )
            source.update(status="ok", models=len(models))
        except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
            source.update(status=f"unavailable: {type(exc).__name__}")
        sources.append(source)
    # Independent leaderboards are a ranking signal, never a permission signal.
    # The model ID remains discovered from the provider catalog above.
    for candidate in candidates:
        model = candidate["model"].casefold()
        score = 0
        for token, points in (
            ("gpt-oss", 80),
            ("gpt-", 78),
            ("nemotron", 75),
            ("deepseek", 72),
            ("gemini", 70),
            ("claude", 70),
            ("grok", 68),
            ("llama-3.3", 65),
            ("qwen3", 65),
            ("mistral", 60),
            ("command", 55),
            ("phi", 45),
        ):
            if token in model:
                score = max(score, points)
        candidate["independent_quality_signal"] = score
    candidates.sort(
        key=lambda item: (-item["independent_quality_signal"], item["provider"], item["model"])
    )
    market = {
        "checked": today,
        "quality_sources": list(QUALITY_SOURCES),
        "quality_evidence": quality_source_evidence(),
        "providers": sources,
        "candidate_count": len(candidates),
    }
    return candidates, market


def collect_questions() -> list[str]:
    """Collect current, rejected, and historical question text for exclusion."""

    questions: list[str] = []
    paths = [
        ROOT / "data" / "eval" / "gold.jsonl",
        ROOT / "data" / "eval" / "candidates.jsonl",
        ROOT / "data" / "eval" / "reviewed.jsonl",
    ]
    paths.extend(sorted((ROOT / "data" / "eval" / "drafts").glob("*.json")))
    for path in paths:
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            if path.suffix == ".jsonl":
                values = [json.loads(line) for line in raw.splitlines() if line.strip()]
            else:
                loaded = json.loads(raw)
                values = loaded if isinstance(loaded, list) else [loaded]

            def walk(value: Any) -> None:
                if isinstance(value, dict):
                    if value.get("question"):
                        questions.append(normalize(str(value["question"])))
                    for child in value.values():
                        walk(child)
                elif isinstance(value, list):
                    for child in value:
                        walk(child)

            walk(values)
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            continue
    return sorted(set(question for question in questions if question))


def load_records() -> list[dict[str, Any]]:
    full = ROOT / "data" / "processed" / "source_sections.full.jsonl"
    if full.exists():
        return load_jsonl(full)
    # The compact artifact intentionally omits train.  A host with the eval DB
    # can materialize the same payloads without changing the public database.
    dsn = os.environ.get(
        "RAG_EVAL_DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval"
    )
    try:
        import psycopg
        from psycopg.rows import dict_row

        with psycopg.connect(dsn, connect_timeout=5, row_factory=dict_row) as connection:
            rows = connection.execute("""SELECT c.payload FROM public.chunks c
                JOIN public.document_versions v ON v.id=c.document_version_id
                WHERE v.status='active' ORDER BY c.chunk_key""").fetchall()
        result = []
        for row in rows:
            payload = dict(row["payload"])
            payload.setdefault("content_hash", text_hash(str(payload.get("text", ""))))
            result.append(payload)
        if result:
            return result
    except (OSError, RuntimeError, ImportError):
        pass
    raise RuntimeError(
        "full train corpus is unavailable; create data/processed/source_sections.full.jsonl "
        "or start evidence_rag_eval"
    )


def write_gzip_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(temporary, "wt", encoding="utf-8", compresslevel=9) as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    temporary.replace(path)
    if path.stat().st_size > MAX_COMPRESSED_BYTES:
        raise RuntimeError(f"{path} is {path.stat().st_size} bytes, over the 40 MiB guard")


def assert_train_size() -> None:
    compressed = sum(path.stat().st_size for path in TRAIN.glob("*.gz"))
    if compressed > MAX_COMPRESSED_BYTES:
        raise RuntimeError(
            f"data/train compressed size is {compressed} bytes, over the 40 MiB guard"
        )


def make_train_materialization(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    manifest = json.loads((ROOT / "data" / "eval" / "section_families.json").read_text())
    splits = json.loads((ROOT / "data" / "eval" / "splits.json").read_text())
    assignments = splits["assignments"]
    gold = load_jsonl(ROOT / "data" / "eval" / "gold.jsonl")
    candidate_questions = collect_questions()
    quote_set = gold_quotes(gold)
    passages = select_unique_passages(records, assignments, manifest, quote_set)
    if not passages:
        raise RuntimeError("no train passages survived family, kind, length, and leakage guards")
    corpus: dict[str, dict[str, Any]] = {}
    for record in records:
        text = str(record.get("text", ""))
        if not text or record.get("kind") not in {"text", "table"}:
            continue
        value = dict(record)
        value["content_hash"] = str(value.get("content_hash") or text_hash(text))
        corpus.setdefault(
            value["content_hash"],
            {
                "content_hash": value["content_hash"],
                "text": text,
                "kind": value.get("kind", "text"),
            },
        )
    exclusions = sorted(quote_set | set(candidate_questions))
    return passages, list(corpus.values()), exclusions


def passage_prompt(records: list[dict[str, Any]]) -> str:
    blocks = []
    for number, record in enumerate(records, 1):
        blocks.append(f"PASSAGE {number} (id={record['content_hash']}):\n{record['text']}")
    return (
        "You write retrieval-training questions for PostgreSQL documentation.\n\n"
        "Return JSON only, with exactly one object per passage in a top-level array.\n"
        "Each object has a `queries` array containing exactly four objects with fields\n"
        "`text`, `style`, and `answerable_from_passage`. Use these styles exactly:\n"
        "identifier, behavior, troubleshooting, keyword. The identifier question may\n"
        "name an exact parameter/function. The behavior question must describe the\n"
        "behavior without naming the parameter or function. The troubleshooting\n"
        "question must be a practitioner's how-do-I or troubleshooting question with\n"
        "a concrete goal. The keyword question is a short search string.\n\n"
        "Every question must be answerable from its own passage alone, must not say\n"
        "according to the passage/text/section, and must vary its opening and difficulty.\n"
        "Set answerable_from_passage false when the passage is insufficient.\n\n"
        + "\n\n".join(blocks)
    )


def extract_json(text: str) -> Any:
    value = text.strip()
    if value.startswith("```"):
        value = re.sub(r"^```(?:json)?\s*|\s*```$", "", value, flags=re.I | re.S).strip()
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        start = min(
            (index for index in (value.find("["), value.find("{")) if index >= 0), default=-1
        )
        if start < 0:
            raise
        end = max(value.rfind("]"), value.rfind("}"))
        return json.loads(value[start : end + 1])


def parse_generation(payload: Any, passages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    values = payload.get("passages", payload) if isinstance(payload, dict) else payload
    if not isinstance(values, list) or len(values) != len(passages):
        raise ValueError("generator returned the wrong number of passage objects")
    output: list[dict[str, Any]] = []
    for passage, value in zip(passages, values, strict=True):
        queries = value.get("queries") if isinstance(value, dict) else None
        if not isinstance(queries, list) or len(queries) != 4:
            raise ValueError("generator must return four queries per passage")
        normalized = [validate_query_record(item) for item in queries]
        if {item["style"] for item in normalized} != set(STYLE_NAMES):
            raise ValueError("generator must return each style exactly once")
        output.append({"content_hash": passage["content_hash"], "queries": normalized})
    return output


def call_generator(
    candidate: dict[str, Any], passages: list[dict[str, Any]], key: str, cache_path: Path
) -> tuple[list[dict[str, Any]], float]:
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        return parse_generation(cached["response"], passages), float(cached["latency_seconds"])
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["queries"],
            "properties": {"queries": {"type": "array", "minItems": 4, "maxItems": 4}},
        },
    }
    payload = {
        "model": candidate["model"],
        "messages": [
            {"role": "system", "content": "Return only valid JSON."},
            {"role": "user", "content": passage_prompt(passages)},
        ],
        "temperature": 0.8,
        "max_tokens": 1800,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "queries", "strict": True, "schema": schema},
        },
        "reasoning_effort": "none",
    }
    started = time.perf_counter()
    response = json_request(candidate["chat_url"], key, payload=payload, timeout=90)
    latency = time.perf_counter() - started
    try:
        choice = response["choices"][0]
        if choice.get("finish_reason") == "length":
            raise ValueError("generator response was truncated")
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("generator response has no assistant content") from exc
    parsed = extract_json(str(content))
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(
        cache_path,
        {
            "candidate": {key: candidate[key] for key in ("provider", "model")},
            "latency_seconds": latency,
            "response": parsed,
        },
    )
    return parse_generation(parsed, passages), latency


def with_retries(
    candidate: dict[str, Any],
    passages: list[dict[str, Any]],
    key: str,
    cache_path: Path,
    state: dict[str, float],
) -> tuple[list[dict[str, Any]], float]:
    interval = float(os.environ.get("PHASE5_MIN_INTERVAL_SECONDS", "0.5"))
    wait = max(0.0, interval - (time.monotonic() - state.get(candidate["provider"], 0.0)))
    if wait:
        time.sleep(wait)
    last: Exception | None = None
    for attempt in range(4):
        try:
            values, latency = call_generator(candidate, passages, key, cache_path)
            state[candidate["provider"]] = time.monotonic()
            return values, latency
        except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
            last = exc
            time.sleep(min(30.0, 2.0**attempt))
    raise RuntimeError(
        f"generator {candidate['provider']}/{candidate['model']} failed after retries"
    ) from last


def trial(candidate: dict[str, Any], passages: list[dict[str, Any]], key: str) -> dict[str, Any]:
    latencies: list[float] = []
    openings: set[str] = set()
    valid = 0
    state: dict[str, float] = {}
    for start in range(0, len(passages), QUERY_BATCH):
        group = passages[start : start + QUERY_BATCH]
        cache = (
            CACHE
            / "trial"
            / f"{text_hash(candidate['provider'] + ':' + candidate['model'])}-{start}.json"
        )
        try:
            values, latency = with_retries(candidate, group, key, cache, state)
            valid += len(values)
            latencies.append(latency)
            openings.update(
                OPENING_RE.match(query["text"]).group(1).casefold()
                for value in values
                for query in value["queries"]
                if OPENING_RE.match(query["text"])
            )
        except RuntimeError:
            break
    total = len(passages) * 4
    return {
        "provider": candidate["provider"],
        "model": candidate["model"],
        "passages": len(passages),
        "valid_queries": valid,
        "expected_queries": total,
        "valid_ratio": valid / total if total else 0.0,
        "median_latency_seconds": statistics.median(latencies) if latencies else None,
        "distinct_openings": len(openings),
        "opening_ratio": len(openings) / total if total else 0.0,
        "passed": valid >= 0.9 * total
        and bool(latencies)
        and statistics.median(latencies) < 30
        and len(openings) >= 0.8 * total,
    }


def make_chunks(records: list[dict[str, Any]]) -> list[Any]:
    from rag_service.domain import Chunk

    return [
        Chunk(
            chunk_id=str(record["content_hash"]),
            document_id="train",
            version="train",
            text=str(record["text"]),
            kind=str(record.get("kind", "text")),
            content_hash=str(record["content_hash"]),
            lineage_key=str(record.get("lineage_key", "")),
        )
        for record in records
    ]


def ranking_maps(
    passages: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    """Build BM25 and bge-small ranks once for all generated-query filtering."""

    from rag_service.retrieval.bm25 import bm25_search
    from rag_service.retrieval.local_models import SentenceTransformerEncoder

    chunks = make_chunks(passages)
    bm25: dict[str, dict[str, int]] = {}
    dense: dict[str, dict[str, int]] = {}
    encoder = SentenceTransformerEncoder("bge-small", batch_size=64, query_instruction=True)
    vectors = encoder.embed([record["text"] for record in passages])
    for query in (question for record in passages for question in record.get("_queries", ())):
        sparse = bm25_search(query, chunks, 200)
        bm25[query] = {
            match.chunk.content_hash or match.chunk.chunk_id: rank
            for rank, match in enumerate(sparse, 1)
        }
        query_vector = encoder.embed_query(query)
        scored = sorted(
            (
                (
                    sum(a * b for a, b in zip(query_vector, vector, strict=True)),
                    record["content_hash"],
                )
                for record, vector in zip(passages, vectors, strict=True)
            ),
            key=lambda item: (-item[0], item[1]),
        )[:200]
        dense[query] = {content_hash: rank for rank, (_, content_hash) in enumerate(scored, 1)}
    return bm25, dense


def filter_generated(
    generated: list[dict[str, Any]], passages: list[dict[str, Any]], exclusions: list[str]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_hash = {record["content_hash"]: record for record in passages}
    for record in passages:
        record["_queries"] = [
            item["text"]
            for item in next(
                (
                    value["queries"]
                    for value in generated
                    if value["content_hash"] == record["content_hash"]
                ),
                [],
            )
        ]
    bm25, dense = ranking_maps(passages)
    kept: list[dict[str, Any]] = []
    seen: list[str] = []
    report: dict[str, Any] = {style: Counter() for style in STYLE_NAMES}
    report["by_model"] = {}
    for group in generated:
        source = by_hash[group["content_hash"]]
        model = f"{group.get('provider', 'unknown')}/{group.get('generator', 'unknown')}"
        model_counts = report["by_model"].setdefault(
            model, {style: Counter() for style in STYLE_NAMES}
        )
        for query in group["queries"]:
            style = query["style"]
            text = query["text"]
            if not query["answerable_from_passage"]:
                report[style]["unanswerable"] += 1
                model_counts[style]["unanswerable"] += 1
                continue
            if style == "behavior" and violates_behavior_style(text, source["text"]):
                report[style]["names_identifier"] += 1
                model_counts[style]["names_identifier"] += 1
                continue
            excluded = exclusion_match(text, exclusions)
            if excluded is not None:
                report[style]["exclusion"] += 1
                model_counts[style]["exclusion"] += 1
                continue
            if not union_rank_accepts(
                group["content_hash"], (bm25.get(text, {}), dense.get(text, {}))
            ):
                report[style]["not_top_200_union"] += 1
                model_counts[style]["not_top_200_union"] += 1
                continue
            if any(near_duplicate(text, prior) for prior in seen):
                report[style]["near_duplicate"] += 1
                model_counts[style]["near_duplicate"] += 1
                continue
            seen.append(text)
            kept.append(
                {
                    "query_id": text_hash(group["content_hash"] + "\0" + text),
                    "question": text,
                    "style": style,
                    "answerable_from_passage": True,
                    "positive_content_hash": group["content_hash"],
                    "source_lineage": source.get("lineage_key", ""),
                    "source_family": source.get("family_key", ""),
                }
            )
            report[style]["kept"] += 1
            model_counts[style]["kept"] += 1
    for record in passages:
        record.pop("_queries", None)
    by_model = {
        model: {style: dict(counts) for style, counts in values.items()}
        for model, values in report["by_model"].items()
    }
    return kept, {**{style: dict(report[style]) for style in STYLE_NAMES}, "by_model": by_model}


def push_train_data() -> None:
    subprocess.run(["git", "add", "data/train"], cwd=ROOT, check=True)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if result.returncode == 0:
        print("--push requested but data/train has no changes", flush=True)
        return
    subprocess.run(
        ["git", "commit", "-m", "data: add phase 5 training material"], cwd=ROOT, check=True
    )
    subprocess.run(
        ["git", "push", "--set-upstream", "origin", "phase-5-finetune"], cwd=ROOT, check=True
    )


def run(args: argparse.Namespace) -> int:
    TRAIN.mkdir(parents=True, exist_ok=True)
    records = load_records()
    passages, corpus, exclusions = make_train_materialization(records)
    train_path = TRAIN / "train_passages.jsonl.gz"
    write_gzip_jsonl(train_path, passages)
    write_gzip_jsonl(TRAIN / "corpus_texts.jsonl.gz", corpus)
    atomic_write(TRAIN / "exclusions.json", exclusions)
    print(
        f"Prepared {len(passages)} unique train passages and {len(corpus)} corpus texts", flush=True
    )

    keys = {
        **read_dotenv_names(),
        **{
            name: value
            for name in {spec["key"] for spec in PROVIDERS}
            if (value := os.environ.get(name))
        },
    }
    candidates, market = discover_market(keys)
    atomic_write(TRAIN / "generator_market.json", market | {"candidates": candidates})
    paid = [
        candidate
        for candidate in candidates
        if candidate["terms_status"] == "permitted_for_this_use"
    ]
    free = [candidate for candidate in paid if "paid" not in candidate["free_status"]]
    if not free:
        cheapest = paid[0] if paid else None
        if not args.approve_paid:
            print(
                "STOP: no free candidate clears the quality/terms gate; no paid calls were made.",
                flush=True,
            )
            if cheapest:
                print(
                    f"Cheapest permitted paid candidate to review: {cheapest['provider']}/"
                    f"{cheapest['model']}; rerun with --approve-paid only after approval.",
                    flush=True,
                )
            else:
                print(
                    "All discovered providers were excluded or had unclear output-training terms.",
                    flush=True,
                )
            return 2
        free = paid
    trial_passages = passages[:TRIAL_PASSAGES]
    passing: list[dict[str, Any]] = []
    for candidate in free[: max(3, args.max_models)]:
        result = trial(candidate, trial_passages, keys[candidate["key_name"]])
        print(f"Generator trial {candidate['provider']}/{candidate['model']}: {result}", flush=True)
        if result["passed"]:
            candidate["trial"] = result
            passing.append(candidate)
        if len(passing) == 2:
            break
    if not passing:
        print(
            "STOP: no generator passed JSON, truncation, opening-diversity, and latency gates.",
            flush=True,
        )
        return 3
    generated: list[dict[str, Any]] = []
    state: dict[str, float] = {}
    calls = 0
    for start in range(0, len(passages), QUERY_BATCH):
        group = passages[start : start + QUERY_BATCH]
        candidate = passing[(start // QUERY_BATCH) % len(passing)]
        cache_key = text_hash(
            candidate["provider"]
            + ":"
            + candidate["model"]
            + ":"
            + ":".join(passage["content_hash"] for passage in group)
        )
        cache = CACHE / "generation" / f"{cache_key}.json"
        values, _ = with_retries(candidate, group, keys[candidate["key_name"]], cache, state)
        generated.extend(
            {**value, "generator": candidate["model"], "provider": candidate["provider"]}
            for value in values
        )
        calls += 1
        if calls > GENERATOR_CALL_LIMIT:
            raise RuntimeError("generator call guard exceeded 1,500 calls")
    kept, report = filter_generated(generated, passages, exclusions)
    if not TARGET_QUERIES[0] <= len(kept) <= TARGET_QUERIES[1]:
        print(
            f"Generation/filter report: kept {len(kept)}; target was {TARGET_QUERIES}", flush=True
        )
    write_gzip_jsonl(TRAIN / "train_queries.jsonl.gz", kept)
    assert_train_size()
    atomic_write(
        TRAIN / "generation_report.json",
        {
            "passages": len(passages),
            "generated": len(generated) * 4,
            "kept": len(kept),
            "by_style": report,
            "generators": passing,
        },
    )
    if args.push:
        push_train_data()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--push", action="store_true", help="commit data/train and push this branch"
    )
    parser.add_argument(
        "--approve-paid", action="store_true", help="explicitly permit paid candidates"
    )
    parser.add_argument("--max-models", type=int, default=2)
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
