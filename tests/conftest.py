"""Repository-wide disposable PostgreSQL database fixture."""

from __future__ import annotations

import os
from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo


@pytest.fixture(scope="session", autouse=True)
def disposable_database() -> Iterator[None]:
    """Create one uniquely named database for every database-backed test run."""

    admin_url = os.getenv("RAG_TEST_ADMIN_DATABASE_URL")
    configured_url = os.getenv("RAG_TEST_DATABASE_URL")
    configured_run = os.getenv("RAG_TEST_RUN_DATABASE")
    if admin_url is None:
        if configured_url is not None or configured_run is not None:
            raise RuntimeError(
                "Use RAG_TEST_ADMIN_DATABASE_URL; RAG_TEST_DATABASE_URL and "
                "RAG_TEST_RUN_DATABASE are fixture-owned outputs"
            )
        yield
        return

    admin_name = str(conninfo_to_dict(admin_url).get("dbname") or "")
    if admin_name not in {"postgres", "template1"}:
        raise RuntimeError(
            "RAG_TEST_ADMIN_DATABASE_URL must point to postgres or template1, "
            f"not {admin_name or '<empty>'}"
        )
    if configured_url is not None or configured_run is not None:
        raise RuntimeError(
            "Do not preconfigure RAG_TEST_DATABASE_URL or RAG_TEST_RUN_DATABASE; "
            "the fixture owns both values"
        )

    name = "rag_test_" + uuid4().hex
    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(name)))
        print(f"\nCreated disposable database: {name}")
        try:
            with pytest.MonkeyPatch.context() as env:
                env.setenv("RAG_TEST_DATABASE_URL", make_conninfo(admin_url, dbname=name))
                env.setenv("RAG_TEST_RUN_DATABASE", name)
                yield
        finally:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
            print(f"Dropped disposable database: {name}")
