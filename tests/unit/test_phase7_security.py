"""Phase 7 API authentication, limits, side-channel and mutation tests."""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import jwt
import pytest

from rag_service.api.app import create_app
from rag_service.api.security import JWTVerifier, enforce_payload_limits
from rag_service.application import RagApplication
from rag_service.domain import AccessPolicy, Chunk
from rag_service.generation import ExtractiveAnswerGenerator
from rag_service.retrieval import RetrievalFilters, RetrievalResult, ScopeResult, ScoredChunk
from rag_service.settings import Settings


def make_token(
    settings: Any,
    *,
    subject: str = "alice",
    groups: list[str] | None = None,
    roles: list[str] | None = None,
    expires: int = 300,
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "sub": subject,
            "groups": groups or [],
            "roles": roles or ["reader"],
            "iat": now,
            "exp": now + expires,
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


def make_app(*, settings: Settings | None = None, slow: bool = False) -> tuple[Any, Settings, Any]:
    settings = settings or Settings(
        dense_model="hash-v1", reranker_model="token-overlap", rate_limit_requests=100
    )
    chunk = Chunk(
        "c1",
        "manual",
        "pg-16",
        "The max_workers default is 8.",
        access_policy=AccessPolicy(public=True),
    )
    result = RetrievalResult(
        (ScoredChunk(chunk, hybrid_score=0.9),),
        ScopeResult(RetrievalFilters(product_version="pg-16"), versions=("pg-16",)),
        "trace",
        (),
    )

    class Retriever:
        index = object()

        async def retrieve_detailed(self, *args: Any, **kwargs: Any) -> RetrievalResult:
            if slow:
                await asyncio.sleep(0.1)
            return result

    pipeline = MagicMock()
    pipeline.ingest.return_value = SimpleNamespace(
        document_id="new",
        version="pg-16",
        content_hash="hash",
        ingestion_id="ingest-1",
        chunk_count=1,
        already_ingested=False,
        revision=1,
    )
    retriever: Any = Retriever()
    application = RagApplication(
        pipeline, retriever, ExtractiveAnswerGenerator(minimum_score=0.0), verify_generation=True
    )
    return create_app(application, settings), settings, pipeline


async def request(app: Any, method: str, path: str, **kwargs: Any) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://local") as client:
        return await client.request(method, path, **kwargs)


def test_jwt_requires_strict_claims_and_hs256() -> None:
    settings = Settings()
    verifier = JWTVerifier(settings)
    now = int(time.time())
    base = {"sub": "alice", "groups": ["sre"], "roles": ["reader"], "iat": now, "exp": now + 60}
    valid = jwt.encode(base, settings.jwt_secret, algorithm="HS256")
    assert verifier.verify(valid).groups == ("sre",)
    for token in (
        jwt.encode({**base, "exp": now - 1}, settings.jwt_secret, algorithm="HS256"),
        jwt.encode(base, settings.jwt_secret + "x" * 16, algorithm="HS384"),
        jwt.encode(base, "wrong-secret-that-is-long-enough-for-testing", algorithm="HS256"),
        jwt.encode({**base, "sub": None}, settings.jwt_secret, algorithm="HS256"),
        jwt.encode(
            {key: value for key, value in base.items() if key != "iat"},
            settings.jwt_secret,
            algorithm="HS256",
        ),
    ):
        with pytest.raises(ValueError):
            verifier.verify(token)
    tampered = valid[:-1] + ("a" if valid[-1] != "a" else "b")
    with pytest.raises(ValueError):
        verifier.verify(tampered)
    none_token = jwt.encode(base, key="", algorithm="none")
    with pytest.raises(ValueError):
        verifier.verify(none_token)
    assert len(settings.jwt_secret.encode()) >= 32


async def test_health_public_query_requires_verified_token_and_spoof_is_ignored() -> None:
    app, settings, _ = make_app()
    health = await request(app, "GET", "/v1/health")
    assert health.status_code == 200
    missing = await request(app, "POST", "/v1/query", json={"query": "default"})
    assert missing.status_code == 401
    token = make_token(settings, subject="alice", groups=["sre"])
    response = await request(
        app,
        "POST",
        "/v1/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "default", "principal": "mallory", "groups": ["admins"]},
    )
    assert response.status_code == 200
    assert response.json()["abstained"] is False


async def test_mutation_roles_and_job_alias_are_enforced() -> None:
    app, settings, pipeline = make_app()
    reader = make_token(settings, roles=["reader"])
    admin = make_token(settings, roles=["ingest"])
    body = {"document_id": "new", "version": "pg-16", "text": "bounded text"}
    denied = await request(
        app, "POST", "/v1/documents", headers={"Authorization": f"Bearer {reader}"}, json=body
    )
    assert denied.status_code == 403
    accepted = await request(
        app, "POST", "/v1/documents", headers={"Authorization": f"Bearer {admin}"}, json=body
    )
    assert accepted.status_code in {200, 422}
    assert pipeline.ingest.called
    deleted = await request(
        app, "DELETE", "/v1/documents/new", headers={"Authorization": f"Bearer {reader}"}
    )
    assert deleted.status_code == 403
    jobs = await request(
        app, "GET", "/v1/jobs/unknown", headers={"Authorization": f"Bearer {reader}"}
    )
    assert jobs.status_code == 403


async def test_expired_and_tampered_http_tokens_are_401() -> None:
    app, settings, _ = make_app()
    now = int(time.time())
    expired = jwt.encode(
        {"sub": "a", "groups": [], "roles": ["reader"], "iat": now - 10, "exp": now - 1},
        settings.jwt_secret,
        algorithm="HS256",
    )
    for token in (expired, "not.a.jwt"):
        response = await request(
            app,
            "POST",
            "/v1/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": "default"},
        )
        assert response.status_code == 401


def test_input_limits_are_413_and_pydantic_bounds_remain_strict() -> None:
    settings = Settings(
        max_query_chars=3,
        max_document_chars=5,
        max_section_chars=4,
        max_sections=1,
        max_metadata_keys=1,
        max_metadata_depth=1,
    )
    with pytest.raises(Exception, match="query"):
        enforce_payload_limits(
            type("Payload", (), {"query": "long", "sections": [], "text": None, "metadata": {}})(),
            settings,
        )
    with pytest.raises(Exception, match="document"):
        enforce_payload_limits(
            type(
                "Payload", (), {"query": "ok", "sections": [], "text": "123456", "metadata": {}}
            )(),
            settings,
        )


async def test_rate_limit_and_request_timeout() -> None:
    rate_settings = Settings(
        dense_model="hash-v1",
        reranker_model="token-overlap",
        rate_limit_requests=1,
        rate_limit_window_seconds=60,
    )
    app, settings, _ = make_app(settings=rate_settings)
    token = make_token(settings)
    headers = {"Authorization": f"Bearer {token}"}
    first = await request(app, "POST", "/v1/query", headers=headers, json={"query": "default"})
    second = await request(app, "POST", "/v1/query", headers=headers, json={"query": "default"})
    assert first.status_code == 200 and second.status_code == 429
    assert second.headers["retry-after"]
    slow_settings = Settings(
        dense_model="hash-v1",
        reranker_model="token-overlap",
        request_timeout_seconds=0.01,
        rate_limit_requests=100,
    )
    slow_app, slow_settings, _ = make_app(settings=slow_settings, slow=True)
    slow_token = make_token(slow_settings)
    response = await request(
        slow_app,
        "POST",
        "/v1/query",
        headers={"Authorization": f"Bearer {slow_token}"},
        json={"query": "default"},
    )
    assert response.status_code == 504


def test_acl_policy_update_cache_parent_and_deletion_are_immediate() -> None:
    from rag_service.ingestion import DeterministicChunker, IngestionPipeline
    from rag_service.retrieval import InMemoryHybridIndex

    index = InMemoryHybridIndex()
    pipeline = IngestionPipeline(
        DeterministicChunker(max_tokens=20, overlap_tokens=0), index_writer=index
    )
    pipeline.ingest(
        "doc", "secret text", "pg-16", access_policy=AccessPolicy(principals=("alice",))
    )
    assert index.available_versions(RetrievalFilters(principal="bob")) == {}
    pipeline.ingest("doc", "secret text", "pg-16", access_policy=AccessPolicy(principals=("bob",)))
    assert index.available_versions(RetrievalFilters(principal="alice")) == {}
    assert index.available_versions(RetrievalFilters(principal="bob")) == {"doc": ("pg-16",)}
    parent = Chunk(
        "parent", "doc", "pg-16", "parent", access_policy=AccessPolicy(principals=("bob",))
    )
    child = Chunk(
        "child",
        "doc",
        "pg-16",
        "child",
        parent_id="parent",
        access_policy=AccessPolicy(principals=("alice",)),
    )
    index.upsert((parent, child))
    expanded = index.expand_parents(
        (ScoredChunk(child, hybrid_score=1),), filters=RetrievalFilters(principal="alice")
    )
    assert {match.chunk.chunk_id for match in expanded} == {"child"}
    pipeline.delete_document("doc", "pg-16")
    assert index.available_versions(RetrievalFilters(principal="bob")) == {}


def test_acl_is_applied_before_dense_bm25_hybrid_parent_and_trace_paths() -> None:
    from rag_service.retrieval import InMemoryHybridIndex

    index = InMemoryHybridIndex()
    public = Chunk(
        "public", "doc", "pg-16", "public authorization evidence",
        access_policy=AccessPolicy(public=True),
    )
    private = Chunk(
        "private", "doc", "pg-16", "private authorization evidence",
        access_policy=AccessPolicy(principals=("alice",)),
    )
    index.upsert((public, private), dense_vectors=((1.0,), (1.0,)), sparse_vectors=({}, {}))
    denied = RetrievalFilters(principal="bob")
    assert {
        m.chunk.chunk_id for m in index.dense_search((1.0,), top_k=5, filters=denied)
    } == {"public"}
    assert {
        m.chunk.chunk_id
        for m in index.sparse_search("authorization", top_k=5, filters=denied)
    } == {"public"}
    assert {
        m.chunk.chunk_id
        for m in index.search((1.0,), {}, top_k=5, alpha=1.0, filters=denied)
    } == {"public"}
    index.save_trace("trace", "authorization", denied, [{"candidates": ["public"]}])
    assert "private" not in str(index.traces["trace"])
    assert set(index.available_versions(denied)) == {"doc"}


async def test_restricted_query_is_normal_200_abstention_and_scope_is_not_leaked() -> None:
    settings = Settings(dense_model="hash-v1", reranker_model="token-overlap")
    result = RetrievalResult(
        (), ScopeResult(RetrievalFilters(product_version="pg-17"), versions=()), "trace", ()
    )
    retriever = MagicMock()
    retriever.index = object()
    retriever.retrieve_detailed = AsyncMock(return_value=result)
    app = create_app(
        RagApplication(None, retriever, ExtractiveAnswerGenerator(), verify_generation=True),
        settings,
    )
    token = make_token(settings, subject="bob")
    response = await request(
        app,
        "POST",
        "/v1/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "secret", "product_version": "pg-17"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "not found" and data["abstained"] is True
    assert data["scope_versions"] == [] and data["matches"] == []
