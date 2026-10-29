"""Small findings-first Streamlit client for the Evidence RAG API."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx
import jwt


def _token(secret: str, principal: str, groups: list[str], roles: list[str]) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "sub": principal,
            "groups": groups,
            "roles": roles,
            "iat": now,
            "exp": now + 3600,
        },
        secret,
        algorithm="HS256",
    )


def _get(client: httpx.Client, path: str) -> dict[str, Any]:
    response = client.get(path)
    response.raise_for_status()
    return response.json()


def _post(client: httpx.Client, path: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(path, json=payload)
    response.raise_for_status()
    return response.json()


def main() -> None:
    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError(
            "The UI requires the optional 'ui' dependency: pip install -e '.[ui]'"
        ) from exc

    st.set_page_config(page_title="Evidence RAG", layout="wide")
    st.title("Evidence RAG")
    st.caption("Findings-first demo: every answer exposes version, quotes, support, and cost.")

    api_url = st.sidebar.text_input("API URL", os.getenv("RAG_UI_API_URL", "http://127.0.0.1:8000"))
    secret = st.sidebar.text_input(
        "Local JWT secret",
        os.getenv("RAG_JWT_SECRET", "phase8-demo-secret-change-me-32-bytes!!"),
        type="password",
    )
    preset = st.sidebar.selectbox(
        "JWT preset",
        ("public reader", "operations reader", "admin"),
    )
    presets = {
        "public reader": ("demo-public", [], ["reader"]),
        "operations reader": ("demo-operator", ["operations"], ["reader"]),
        "admin": ("demo-admin", ["operations"], ["admin", "reader"]),
    }
    principal, groups, roles = presets[preset]
    token = _token(secret, principal, groups, roles)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        with httpx.Client(base_url=api_url.rstrip("/"), headers=headers, timeout=15.0) as client:
            coverage = _get(client, "/v1/corpus/coverage")
            summary = _get(client, "/v1/traces/summary")
    except httpx.HTTPError as exc:
        st.error(f"API unavailable: {exc}")
        st.stop()

    missing = int(coverage.get("missing_dense_chunks", 0))
    if missing:
        st.warning(
            f"Vector coverage is partial: {coverage.get('vector_linked_chunks', 0):,} of "
            f"{coverage.get('total_active_chunks', 0):,} active chunks are vector-linked; "
            f"{missing:,} lack verified dense vectors. Provenance: {coverage.get('provenance')}."
        )
    else:
        st.success("All active demo chunks have deterministic vectors.")

    coverage_columns = st.columns(5)
    for column, label, key in zip(
        coverage_columns,
        ("Active chunks", "Vector-linked", "Embeddings", "Missing dense", "Trace cost"),
        (
            "total_active_chunks",
            "vector_linked_chunks",
            "embedding_records",
            "missing_dense_chunks",
            "cost_usd",
        ),
        strict=True,
    ):
        value = coverage.get(key, summary.get(key, 0))
        column.metric(label, f"{value:,}" if isinstance(value, int) else f"${float(value):.6f}")

    query = st.text_area("Question", "What does WAL protect?", height=80)
    version = st.selectbox("Product version", ("auto", "pg-15", "pg-16", "pg-17"))
    mode = st.selectbox("Generation mode", ("verified", "extractive", "unverified"))
    compare = st.checkbox("Compare naive sparse retrieval with full hybrid retrieval", value=True)
    if not st.button("Ask", type="primary") or not query.strip():
        return

    payload_base: dict[str, Any] = {
        "query": query,
        "generation_mode": mode,
        "product_version": None if version == "auto" else version,
    }
    search_modes = ("sparse", "hybrid") if compare else ("hybrid",)
    with httpx.Client(base_url=api_url.rstrip("/"), headers=headers, timeout=45.0) as client:
        results = []
        for search_mode in search_modes:
            payload = {**payload_base, "search_mode": search_mode}
            try:
                results.append((search_mode, _post(client, "/v1/query", payload)))
            except httpx.HTTPError as exc:
                st.error(f"{search_mode} query failed: {exc}")
        for search_mode, result in results:
            st.subheader("Naive sparse" if search_mode == "sparse" else "Full hybrid")
            st.write(result.get("answer", ""))
            st.caption(
                f"mode={result.get('generation_mode')} version={result.get('answered_version')} "
                f"abstained={result.get('abstained')} trace={result.get('trace_id')}"
            )
            claims = result.get("claims", [])
            if claims:
                st.markdown("**Claim support**")
                st.dataframe(
                    [
                        {
                            "claim": claim.get("text"),
                            "support": "supported" if claim.get("supported") else "unverified",
                            "quote_verified": all(
                                bool(citation.get("excerpt"))
                                for citation in claim.get("citations", [])
                            ),
                            "included": claim.get("included"),
                            "score": claim.get("support_score"),
                        }
                        for claim in claims
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            for citation in result.get("citations", []):
                st.info(
                    f"{citation.get('document_id')} / {citation.get('product_version')} / "
                    f"{' / '.join(citation.get('section_path', []))}\n\n"
                    f"> {citation.get('excerpt', '')}"
                )
            trace_id = result.get("trace_id")
            if trace_id:
                trace = _get(client, f"/v1/traces/{trace_id}")
                st.markdown("**Stage latency trace (ms)**")
                st.dataframe(
                    [
                        {
                            "stage": stage.get("stage"),
                            "elapsed_ms": stage.get("elapsed_ms"),
                            "candidates": len(stage.get("candidates", [])),
                        }
                        for stage in trace.get("stages", [])
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption(
                    f"Persistent cost ledger: ${float(trace.get('cost_usd', 0.0)):.6f} "
                    f"({trace.get('metadata', {}).get('cost_basis', 'unknown')})"
                )


if __name__ == "__main__":
    main()
