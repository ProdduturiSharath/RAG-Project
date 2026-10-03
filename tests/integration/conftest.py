"""One empty database per pytest run, dropped even when assertions fail."""

import os
from collections.abc import Iterator
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql
from psycopg.conninfo import make_conninfo


@pytest.fixture(scope="session", autouse=True)
def disposable_database() -> Iterator[None]:
    server_url = os.getenv("RAG_TEST_DATABASE_URL")
    if not server_url:
        yield
        return
    # Only connect to the maintenance database, never the supplied application DB.
    admin_url = make_conninfo(server_url, dbname="postgres")
    name = "rag_test_" + uuid4().hex
    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(sql.Identifier(name)))
        print(f"\nCreated disposable database: {name}")
        try:
            with pytest.MonkeyPatch.context() as env:
                env.setenv("RAG_TEST_DATABASE_URL", make_conninfo(server_url, dbname=name))
                env.setenv("RAG_TEST_RUN_DATABASE", name)
                yield
        finally:
            admin.execute(sql.SQL("DROP DATABASE {} WITH (FORCE)").format(sql.Identifier(name)))
            print(f"\nDropped disposable database: {name}")
