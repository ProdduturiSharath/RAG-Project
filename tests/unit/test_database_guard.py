from __future__ import annotations

import pytest

from tests.integration.database import test_database_url


def test_database_url_is_unconfigured_without_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("RAG_TEST_DATABASE_URL", raising=False)
    monkeypatch.delenv("RAG_TEST_RUN_DATABASE", raising=False)
    assert test_database_url() is None


def test_database_url_requires_fixture_run_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "RAG_TEST_DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/rag_test_one"
    )
    monkeypatch.delenv("RAG_TEST_RUN_DATABASE", raising=False)
    with pytest.raises(RuntimeError, match="set together"):
        test_database_url()


def test_database_url_rejects_mismatched_run_name(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "RAG_TEST_DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/rag_test_one"
    )
    monkeypatch.setenv("RAG_TEST_RUN_DATABASE", "rag_test_two")
    with pytest.raises(RuntimeError, match="exact fixture-owned"):
        test_database_url()


def test_database_url_accepts_exact_fixture_target(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "RAG_TEST_DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5432/rag_test_one"
    )
    monkeypatch.setenv("RAG_TEST_RUN_DATABASE", "rag_test_one")
    url = test_database_url()
    assert url is not None
    assert url.endswith("/rag_test_one")
