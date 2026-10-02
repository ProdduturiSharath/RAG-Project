"""Streaming adapter for OpenAI-compatible chat-completion endpoints."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from .models import GeneratedAnswer, GenerationRequest
from .prompting import build_grounded_prompt


class OpenAICompatibleGenerator:
    """Call a hosted chat model without coupling the core to one vendor SDK."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 60.0,
        minimum_score: float = 0.12,
        max_citations: int = 5,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url cannot be empty")
        if not model.strip():
            raise ValueError("model cannot be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if not 0 <= minimum_score <= 1:
            raise ValueError("minimum_score must be between zero and one")
        if max_citations < 1:
            raise ValueError("max_citations must be positive")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.minimum_score = minimum_score
        self.max_citations = max_citations

    async def generate(self, request: GenerationRequest) -> GeneratedAnswer:
        if not self._has_evidence(request):
            return self._abstention()
        pieces: list[str] = []
        async for token in self.stream(request):
            pieces.append(token)
        answer = "".join(pieces).strip()
        if not answer:
            return self._abstention()
        return GeneratedAnswer(
            answer=answer,
            citations=tuple(
                match.citation() for match in request.matches[: self.max_citations]
            ),
            confidence=max(0.0, min(1.0, request.matches[0].final_score)),
            abstained=False,
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        if not self._has_evidence(request):
            yield (
                "I couldn't find enough matching evidence in the indexed documents "
                "to answer that confidently."
            )
            return
        try:
            import httpx  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("LLM streaming requires the optional 'llm' dependency") from exc

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "stream": True,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an evidence-first enterprise assistant. Follow the evidence "
                        "boundaries in the user message exactly."
                    ),
                },
                {"role": "user", "content": build_grounded_prompt(request)},
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choices = event.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield str(content)

    def _has_evidence(self, request: GenerationRequest) -> bool:
        return bool(request.matches) and request.matches[0].final_score >= self.minimum_score

    def _abstention(self) -> GeneratedAnswer:
        return GeneratedAnswer(
            answer=(
                "I couldn't find enough matching evidence in the indexed documents "
                "to answer that confidently."
            ),
            confidence=0.0,
            abstained=True,
        )


__all__ = ["OpenAICompatibleGenerator"]
