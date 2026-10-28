"""Streaming, authorization and verification boundaries without external calls."""

from __future__ import annotations

import asyncio
import json
from dataclasses import replace
from typing import Any

import httpx
import pytest

from rag_service.domain import AccessPolicy, Chunk
from rag_service.generation.models import Claim, GeneratedAnswer, GenerationRequest
from rag_service.generation.openai_compatible import OpenAICompatibleGenerator
from rag_service.generation.prompting import build_grounded_prompt
from rag_service.generation.verification import (
    annotate,
    evidence_confidence,
    lexical_support,
    quote_valid,
    verify_answer,
)
from rag_service.retrieval.models import RetrievalFilters, ScoredChunk


def request() -> GenerationRequest:
    chunk = Chunk(
        "c1",
        "manual",
        "pg-16",
        "The max_workers default is 8.",
        section_path=("Configuration",),
        access_policy=AccessPolicy(public=True),
    )
    return GenerationRequest(
        "What is the max_workers default?",
        (ScoredChunk(chunk, hybrid_score=0.8),),
        answered_version="pg-16",
    )


def answer() -> GeneratedAnswer:
    cite = replace(request().matches[0].citation(), excerpt="The max_workers default is 8.")
    return GeneratedAnswer(
        "The max_workers default is 8.",
        (cite,),
        answered_version="pg-16",
        claims=(Claim("The max_workers default is 8.", (cite,)),),
    )


def response_json() -> dict[str, Any]:
    cite = answer().citations[0]
    return {
        "answer": answer().answer,
        "answered_version": "pg-16",
        "claims": [
            {
                "text": answer().answer,
                "citations": [
                    {
                        "chunk_id": cite.chunk_id,
                        "document_id": cite.document_id,
                        "version": cite.version,
                        "section_path": list(cite.section_path),
                        "quote": cite.excerpt,
                    }
                ],
            }
        ],
    }


def sse_response(*, finish: str = "stop", reasoning: bool = False) -> httpx.Response:
    text = json.dumps(response_json())
    delta = {"content": text[:30]}
    if reasoning:
        delta["reasoning_content"] = "private reasoning"
    events = [
        {"choices": [{"delta": delta}]},
        {"choices": [{"delta": {"content": text[30:]}, "finish_reason": finish}]},
        {
            "choices": [],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        },
    ]
    data = "".join("data: " + json.dumps(e) + "\n\n" for e in events) + "data: [DONE]\n\n"
    return httpx.Response(200, text=data, headers={"Content-Type": "text/event-stream"})


async def test_streaming_consumes_split_events_disables_thinking_and_verifies() -> None:
    captured: list[dict[str, Any]] = []

    def handler(req: httpx.Request) -> httpx.Response:
        assert str(req.url) == "https://api.deepseek.com/chat/completions"
        captured.append(json.loads(req.content))
        return sse_response()

    generator = OpenAICompatibleGenerator(
        api_key="test-only", transport=httpx.MockTransport(handler), min_interval=0
    )
    result = await generator.generate(request())
    assert not result.abstained and result.claims[0].supported
    assert result.answered_version == "pg-16"
    payload = captured[0]
    assert payload["model"] == "deepseek-flash" and payload["stream"] is True
    assert payload["temperature"] == 0 and payload["thinking"] == {"type": "disabled"}
    assert result.metadata["usage"]["completion_tokens"] == 20
    assert "".join([p async for p in generator.stream(request())]) == result.answer


@pytest.mark.parametrize("mode", ["empty", "private", "unauthorized", "wrong-version", "ambiguous"])
async def test_no_network_without_authorized_public_scoped_evidence(mode: str) -> None:
    def forbidden(req: httpx.Request) -> httpx.Response:
        raise AssertionError("policy-denied request reached external transport")

    req = request()
    chunk = req.matches[0].chunk
    if mode == "empty":
        req = replace(req, matches=())
    elif mode in {"private", "unauthorized"}:
        chunk = replace(chunk, access_policy=AccessPolicy(principals=("alice",)))
        req = replace(
            req,
            matches=(replace(req.matches[0], chunk=chunk),),
            filters=RetrievalFilters(principal="alice" if mode == "private" else "guest"),
        )
    elif mode == "wrong-version":
        req = replace(req, answered_version="pg-17")
    else:
        req = replace(req, scope_status="ambiguous")
    generator = OpenAICompatibleGenerator(
        api_key="test-only", transport=httpx.MockTransport(forbidden)
    )
    assert (await generator.generate(req)).abstained


@pytest.mark.parametrize(
    "field,value",
    [
        ("excerpt", "invented quote"),
        ("document_id", "other"),
        ("version", "pg-17"),
        ("section_path", ("Other",)),
        ("chunk_id", "missing"),
    ],
)
def test_quote_checks_every_identity_field(field: str, value: Any) -> None:
    cite = replace(answer().citations[0], **{field: value})
    assert not quote_valid(cite, request())


def test_claim_stripping_numeric_polarity_and_unclaimed_text() -> None:
    good = answer()
    cite = good.citations[0]
    bad = Claim("The max_workers default is 800.", (cite,))
    mixed = replace(good, answer=good.answer + " " + bad.text, claims=(*good.claims, bad))
    result = verify_answer(mixed, request())
    assert result.answer == good.answer
    assert len(result.claims) == 2 and not result.claims[1].supported
    assert result.metadata["stripped_claims"] == 1
    assert lexical_support("max_workers is not 8", cite.excerpt) == 0
    assert lexical_support("max_workers is 800", cite.excerpt) == 0
    assert verify_answer(replace(good, answer="rogue text " + good.answer), request()).abstained
    assert verify_answer(replace(good, answered_version="pg-17"), request()).abstained
    assert verify_answer(good, request(), threshold=1).answer == "not found"
    assert evidence_confidence(replace(request(), query="missing_identifier default?")) == 0


def test_unsupported_claims_and_wrong_quotes_abstain() -> None:
    raw = answer()
    fake = replace(raw.citations[0], excerpt="made up")
    unsupported = replace(raw, claims=(Claim(raw.answer, (fake,)),), citations=(fake,))
    assert not annotate(unsupported, request()).claims[0].supported
    assert verify_answer(unsupported, request()).answer == "not found"


async def test_retries_only_retryable_statuses_and_no_partial_truncation() -> None:
    calls = 0

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(429) if calls == 1 else sse_response()

    generator = OpenAICompatibleGenerator(
        api_key="test-only", min_interval=0, transport=httpx.MockTransport(handler)
    )
    assert not (await generator.generate(request())).abstained
    assert calls == 2
    for status in (400, 401, 403):

        def fail(req: httpx.Request, code: int = status) -> httpx.Response:
            return httpx.Response(code)

        generator.transport = httpx.MockTransport(fail)
        with pytest.raises(RuntimeError, match=str(status)):
            await generator.generate(request())
    generator.transport = httpx.MockTransport(lambda req: sse_response(finish="length"))
    with pytest.raises(ValueError, match="incomplete"):
        await generator.generate(request())
    generator.transport = httpx.MockTransport(lambda req: sse_response(reasoning=True))
    with pytest.raises(ValueError, match="thinking"):
        await generator.generate(request())


async def test_total_deadline_not_just_idle_read_timeout() -> None:
    async def slow(req: httpx.Request) -> httpx.Response:
        await asyncio.sleep(0.1)
        return sse_response()

    generator = OpenAICompatibleGenerator(
        api_key="test-only", timeout_seconds=0.01, transport=httpx.MockTransport(slow)
    )
    with pytest.raises(RuntimeError, match="TimeoutError"):
        await generator.generate(request())


async def test_5xx_backoff_is_exponential_and_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = 0
    delays: list[float] = []

    async def sleep(delay: float) -> None:
        delays.append(delay)

    def handler(req: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(503)

    monkeypatch.setattr(asyncio, "sleep", sleep)
    generator = OpenAICompatibleGenerator(
        api_key="test-only", min_interval=0, transport=httpx.MockTransport(handler)
    )
    with pytest.raises(RuntimeError, match="503"):
        await generator.generate(request())
    assert attempts == 3
    assert [delay for delay in delays if delay > 0] == [1, 2]


def test_prompt_identifies_version_quote_contract_and_injection_boundary() -> None:
    prompt = json.loads(build_grounded_prompt(request()))
    assert prompt["requested_version"] == "pg-16"
    assert prompt["passages"][0]["document_id"] == "manual"
