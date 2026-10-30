"""Integration tests only accept a database provisioned by the pytest fixture."""

import os

from psycopg.conninfo import conninfo_to_dict


def test_database_url() -> str | None:
    url = os.getenv("RAG_TEST_DATABASE_URL")
    run_name = os.getenv("RAG_TEST_RUN_DATABASE")
    if url is None and run_name is None:
        return None
    if url is None or run_name is None:
        raise RuntimeError(
            "RAG_TEST_DATABASE_URL and RAG_TEST_RUN_DATABASE must be set together "
            "by the disposable database fixture"
        )
    name = str(conninfo_to_dict(url).get("dbname") or "")
    if not name.startswith("rag_test_") or name != run_name:
        raise RuntimeError(
            "RAG_TEST_DATABASE_URL must point to the exact fixture-owned rag_test_* "
            "database named by RAG_TEST_RUN_DATABASE"
        )
    return url


test_database_url.__test__ = False  # type: ignore[attr-defined]
