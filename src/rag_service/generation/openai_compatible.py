"""Bounded DeepSeek streaming transport. Serving has no evaluation-cache dependency."""

from __future__ import annotations

import asyncio
import json
import os
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx

from rag_service.retrieval.models import Citation

from .models import Claim, GeneratedAnswer, GenerationRequest
from .prompting import SYSTEM_PROMPT, authorized_request, build_grounded_prompt
from .verification import abstention, verify_answer

ENDPOINT = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-flash"


def deepseek_key(path: Path = Path(".env")) -> str:
    """Read only the selected provider's credential; never source shell input."""
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() == "DEEPSEEK_API_KEY":
                key = value.strip().strip('"').strip("'")
    if not key:
        raise ValueError("DEEPSEEK_API_KEY is required")
    return key


def parse_answer(text: str, metadata: dict[str, Any] | None = None) -> GeneratedAnswer:
    value = json.loads(text)
    if not isinstance(value, dict) or not isinstance(value.get("answer"), str):
        raise ValueError("invalid answer object")
    if value["answer"].strip().casefold() == "not found":
        return abstention(metadata=metadata)
    if not isinstance(value.get("answered_version"), str) or not isinstance(
        value.get("claims"), list
    ):
        raise ValueError("missing version/claims")
    claims = []
    for raw in value["claims"]:
        if not isinstance(raw, dict) or not isinstance(raw.get("text"), str):
            raise ValueError("invalid claim")
        if not isinstance(raw.get("citations"), list):
            raise ValueError("invalid claim citations")
        citations = []
        for cite in raw["citations"]:
            if not isinstance(cite, dict) or not all(
                isinstance(cite.get(k), str)
                for k in ("chunk_id", "document_id", "version", "quote")
            ):
                raise ValueError("invalid citation")
            path = cite.get("section_path")
            if not isinstance(path, list) or not all(isinstance(p, str) for p in path):
                raise ValueError("invalid section_path")
            citations.append(
                Citation(
                    cite["chunk_id"],
                    cite["document_id"],
                    cite["version"],
                    section_path=tuple(path),
                    excerpt=cite["quote"],
                )
            )
        claims.append(Claim(raw["text"], tuple(citations)))
    return GeneratedAnswer(
        value["answer"],
        tuple(dict.fromkeys(c for claim in claims for c in claim.citations)),
        answered_version=value["answered_version"],
        claims=tuple(claims),
        metadata=metadata or {},
    )


class OpenAICompatibleGenerator:
    """Fixed-model, no-thinking provider; every attempt has a 45s wall-clock deadline."""

    external_provider = True

    def __init__(
        self,
        *,
        base_url: str = "https://api.deepseek.com",
        model: str = MODEL,
        api_key: str | None = None,
        timeout_seconds: float = 45.0,
        minimum_score: float = 0.0,
        max_citations: int = 5,
        verified: bool = True,
        threshold: float = 0.0,
        min_interval: float = 0.5,
        max_attempts: int = 3,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        endpoint = base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint += "/chat/completions"
        if model != MODEL or endpoint != ENDPOINT:
            raise ValueError("Phase 6 permits only deepseek-flash at the fixed DeepSeek endpoint")
        if not 0 < timeout_seconds <= 45 or not 1 <= max_attempts <= 3 or min_interval < 0:
            raise ValueError("invalid request bounds")
        self.endpoint, self.model, self.api_key = endpoint, model, api_key
        self.timeout_seconds, self.minimum_score = timeout_seconds, minimum_score
        self.max_citations, self.verified, self.threshold = max_citations, verified, threshold
        self.min_interval, self.max_attempts, self.transport = min_interval, max_attempts, transport
        self._lock = asyncio.Lock()
        self._next_request = 0.0

    def payload(self, request: GenerationRequest) -> dict[str, Any]:
        return {
            "model": MODEL,
            "temperature": 0,
            "stream": True,
            "thinking": {"type": "disabled"},
            "max_tokens": 1600,
            "stream_options": {"include_usage": True},
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_grounded_prompt(request)},
            ],
        }

    async def _throttle(self) -> None:
        async with self._lock:
            await asyncio.sleep(max(0.0, self._next_request - time.monotonic()))
            self._next_request = time.monotonic() + self.min_interval

    async def _completion(self, payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        import httpx

        pieces: list[str] = []
        usage: dict[str, Any] = {}
        finish = None
        done = False
        # httpx's read timeout alone does not cap a slow, continuously emitting SSE stream.
        async with asyncio.timeout(self.timeout_seconds):
            async with httpx.AsyncClient(
                timeout=self.timeout_seconds, transport=self.transport
            ) as client:
                async with client.stream(
                    "POST",
                    self.endpoint,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key or deepseek_key()}",
                        "User-Agent": "Evidence-RAG/phase6",
                        "Accept": "text/event-stream",
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            done = True
                            break
                        event = json.loads(data)
                        if "error" in event:
                            raise ValueError("provider SSE error")
                        if event.get("usage"):
                            usage = event["usage"]
                        for choice in event.get("choices", []):
                            delta = choice.get("delta", {})
                            if delta.get("reasoning_content"):
                                raise ValueError("provider ignored disabled thinking")
                            if delta.get("content"):
                                pieces.append(delta["content"])
                            finish = choice.get("finish_reason") or finish
        if finish != "stop" or not done or not usage:
            raise ValueError("incomplete stream, missing usage, or truncated answer")
        details = usage.get("completion_tokens_details") or {}
        if usage.get("reasoning_tokens", details.get("reasoning_tokens", 0)):
            raise ValueError("nonzero reasoning tokens with disabled thinking")
        return "".join(pieces), usage

    async def generate(self, request: GenerationRequest) -> GeneratedAnswer:
        safe = authorized_request(request, public_only=True)
        if not safe.matches or safe.matches[0].final_score < self.minimum_score:
            return abstention(reason="no_authorized_public_evidence")
        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError(
                "DeepSeek generation requires the optional 'llm' dependency"
            ) from exc
        started = time.perf_counter()
        for attempt in range(self.max_attempts):
            await self._throttle()
            try:
                text, usage = await self._completion(self.payload(safe))
                answer = parse_answer(
                    text,
                    {
                        "usage": usage,
                        "model": MODEL,
                        "latency_seconds": time.perf_counter() - started,
                        "attempts": attempt + 1,
                    },
                )
                return (
                    verify_answer(answer, safe, threshold=self.threshold)
                    if self.verified
                    else answer
                )
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if (status != 429 and not 500 <= status < 600) or attempt + 1 == self.max_attempts:
                    raise RuntimeError(f"DeepSeek request failed: HTTP {status}") from None
                delay = 2.0**attempt
                retry_after = exc.response.headers.get("Retry-After", "")
                if retry_after.isdigit():
                    delay = max(delay, min(30.0, float(retry_after)))
                print(f"DeepSeek HTTP {status}; retry {attempt + 2} in {delay}s", flush=True)
                await asyncio.sleep(delay)
            except (httpx.TransportError, TimeoutError) as exc:
                raise RuntimeError(f"DeepSeek transport failed: {type(exc).__name__}") from None
        raise RuntimeError("DeepSeek attempt limit exhausted")

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        # Buffer structured provider tokens until quote/claim checks have completed.
        answer = await self.generate(request)
        for part in answer.answer.splitlines(keepends=True):
            yield part


__all__ = ["OpenAICompatibleGenerator"]
