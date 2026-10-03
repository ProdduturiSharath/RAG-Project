"""Async Postgres ingestion worker using short SKIP LOCKED leases."""

from __future__ import annotations

import asyncio

from rag_service.api.container import build_application
from rag_service.domain import AccessPolicy, DocumentIdentity, SourceLocation
from rag_service.settings import load_settings

from .postgres import PostgresJobStore, PostgresVersionedStore


async def run_once(store: PostgresVersionedStore, jobs: PostgresJobStore) -> bool:
    job = await asyncio.to_thread(jobs.claim_next, "ingest_document")
    if job is None:
        return False
    job_id = str(job["id"])
    lease_token = str(job["lease_token"])
    try:
        if job["kind"] != "ingest_document":
            raise ValueError(f"unsupported job kind: {job['kind']}")
        payload = job["payload"]
        source = SourceLocation(**payload["source"]) if payload.get("source") else None
        policy = AccessPolicy(**payload["access_policy"]) if payload.get("access_policy") else None
        identity = DocumentIdentity(
            document_id=payload["document_id"],
            title=payload.get("title"),
            source=source,
            access_policy=policy,
        )
        await asyncio.to_thread(
            store.ingest,
            identity,
            payload.get("sections") or payload.get("text") or "",
            payload.get("version"),
            content_hash=payload.get("content_hash"),
            source=source,
            access_policy=policy,
            job_id=job_id,
            lease_token=lease_token,
        )
    except Exception as exc:
        await asyncio.to_thread(jobs.fail, job_id, lease_token, str(exc))
    return True


async def run_forever() -> None:
    settings = load_settings()
    application = build_application(settings)
    if not isinstance(application.pipeline, PostgresVersionedStore):
        raise RuntimeError("worker requires RAG_STORAGE_BACKEND=postgres")
    jobs = PostgresJobStore(settings.database_url, settings.migrations_path)
    while True:
        worked = await run_once(application.pipeline, jobs)
        if not worked:
            await asyncio.sleep(settings.job_poll_seconds)


def main() -> None:
    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
