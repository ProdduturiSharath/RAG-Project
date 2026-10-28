"""Integration tests only accept a database provisioned by the pytest fixture."""

import os

from psycopg.conninfo import conninfo_to_dict


def test_database_url() -> str | None:
    test_url = os.getenv("RAG_TEST_DATABASE_URL")
    url = test_url or os.getenv("RAG_EVAL_DATABASE_URL") or os.getenv("RAG_DATABASE_URL")
    if test_url is not None:
        assert url is not None
        name = conninfo_to_dict(url).get("dbname") or ""
        if name != os.getenv("RAG_TEST_RUN_DATABASE") or not name.startswith("rag_test_"):
            raise RuntimeError("Run integration tests through pytest's disposable database fixture")
    return url


test_database_url.__test__ = False  # type: ignore[attr-defined]
