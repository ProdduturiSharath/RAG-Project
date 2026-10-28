"""JSON/SSE share verified claims and never consult evaluation completions."""

from __future__ import annotations

import importlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from rag_service.application import RagApplication
from rag_service.domain import AccessPolicy
from rag_service.generation.openai_compatible import OpenAICompatibleGenerator
from rag_service.retrieval.models import RetrievalFilters, RetrievalResult, ScopeResult
from rag_service.retrieval.postgres import PostgresHybridIndex
from rag_service.retrieval.service import HybridRetriever
from rag_service.settings import Settings
from rag_service.storage.serialization import chunk_to_payload
from tests.unit.test_phase6_generation import request, sse_response


@pytest.mark.parametrize("private", [False, True])
async def test_json_sse_verified_claims_and_cache_isolation(
    private: bool, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    for name, value in {"RAG_STORAGE_BACKEND": "memory", "RAG_DENSE_MODEL": "hash-v1",
                        "RAG_RERANKER_MODEL": "token-overlap"}.items():
        monkeypatch.setenv(name, value)
    api = importlib.import_module("rag_service.api.app")
    monkeypatch.chdir(tmp_path)
    poison = tmp_path / ".cache/phase6/generation/poison.json"
    poison.parent.mkdir(parents=True)
    poison.write_text('{"answer":"cached poison"}')
    network_calls = []

    def handler(req: httpx.Request) -> httpx.Response:
        network_calls.append(json.loads(req.content))
        return sse_response()

    match = request().matches[0]
    if private:
        match = replace(match, chunk=replace(match.chunk, access_policy=AccessPolicy(
            principals=("alice",))))
    retriever: Any = MagicMock(spec=HybridRetriever)
    retriever.index = object()
    retriever.retrieve_detailed = AsyncMock(return_value=RetrievalResult(
        (match,), ScopeResult(RetrievalFilters(product_version="pg-16"), versions=("pg-16",)),
        "trace", ()))
    generator = OpenAICompatibleGenerator(api_key="test-only", min_interval=0,
        verified=False, transport=httpx.MockTransport(handler))
    application = RagApplication(None, retriever, generator, verify_generation=True)
    settings = Settings()
    app = api.create_app(application, settings)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                                 base_url="http://local") as client:
        payload = {"query": request().query, "product_version": "pg-16", "principal": "alice"}
        json_response = (await client.post("/v1/query", json=payload)).json()
        stream_response = await client.post("/v1/query/stream", json=payload)
    data = [line[6:] for line in stream_response.text.splitlines() if line.startswith("data: ")]
    metadata = json.loads(data[0])
    assert metadata["claims"] == json_response["claims"]
    assert metadata["abstained"] == json_response["abstained"] == private
    assert metadata["answered_version"] == json_response["answered_version"]
    assert len(network_calls) == (0 if private else 2)
    assert "cached poison" not in stream_response.text + json.dumps(json_response)
    if not private:
        assert json_response["claims"][0]["supported"]
        assert json_response["citations"][0]["version"] == "pg-16"


def test_postgres_external_boundary_reads_current_public_acl_and_payload() -> None:
    index = PostgresHybridIndex("postgresql://unused")
    connection = MagicMock()
    index.database = MagicMock()
    index.database.connect.return_value.__enter__.return_value = connection
    connection.execute.return_value.fetchall.return_value = []
    assert index.external_public_chunks(request().matches, request().filters) == ()
    sql, params = connection.execute.call_args.args
    assert "pub.is_public" in sql and "v.status='active'" in sql
    assert params[0] == ["c1"]
    latest = replace(request().matches[0].chunk, text="Current public text")
    connection.execute.return_value.fetchall.return_value = [{"payload": chunk_to_payload(latest)}]
    result = index.external_public_chunks(request().matches, request().filters)
    assert result[0].chunk.text == "Current public text"
    assert result[0].chunk.access_policy is not None and result[0].chunk.access_policy.is_public
