"""Findings-first Streamlit workspace for the Evidence RAG API."""

from __future__ import annotations

import html
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx
import jwt

DEFAULT_QUERY = "What is max_wal_senders used for in PostgreSQL 17?"
_CITATION_MARKER_RE = re.compile(r"\[(\d+)\]")


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


def _load_styles() -> str:
    return Path(__file__).with_name("styles.css").read_text(encoding="utf-8")


def _escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def _cost(value: Any) -> str:
    try:
        return f"${float(value or 0):.6f}"
    except (TypeError, ValueError):
        return "$0.000000"


def _metric_card(label: str, value: str, detail: str) -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{_escape(label)}</div>'
        f'<div class="metric-value">{_escape(value)}</div>'
        f'<div class="metric-detail">{_escape(detail)}</div>'
        "</div>"
    )


def _answer_html(answer: str) -> str:
    escaped = _escape(answer).replace("\n", "<br>")

    def marker(match: re.Match[str]) -> str:
        number = match.group(1)
        return (
            f'<sup class="citation-marker" title="Supporting source {number}" '
            f'aria-label="Supporting source {number}">[{number}]</sup>'
        )

    return _CITATION_MARKER_RE.sub(marker, escaped)


def _render_citation(st: Any, citation: dict[str, Any], number: int) -> None:
    section_path = citation.get("section_path") or []
    section = " / ".join(str(item) for item in section_path) or "Document excerpt"
    source = (
        f"{citation.get('document_id', 'document')}"
        f"  ·  {citation.get('product_version', citation.get('version', 'unknown'))}"
        f"  ·  {section}"
    )
    excerpt = citation.get("excerpt") or "No excerpt was returned."
    st.markdown(
        '<div class="citation-card">'
        f'<div class="citation-source">{number:02d}  {_escape(source)}</div>'
        f'<div class="citation-excerpt">{_escape(excerpt)}</div>'
        "</div>",
        unsafe_allow_html=True,
    )


def _trace_table(stages: list[dict[str, Any]]) -> str:
    rows = "".join(
        "<tr>"
        f"<td>{_escape(stage.get('stage'))}</td>"
        f"<td>{_escape(round(float(stage.get('elapsed_ms', 0)), 1))}</td>"
        f"<td>{_escape(len(stage.get('candidates', [])))}</td>"
        "</tr>"
        for stage in stages
    )
    return (
        '<div class="trace-table-wrap">'
        '<table class="trace-table">'
        "<thead><tr><th>Stage</th><th>Elapsed (ms)</th><th>Candidates</th></tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
        "</div>"
    )


def _render_trace(st: Any, client: httpx.Client, trace_id: str) -> None:
    with st.expander("Diagnostics and trace", expanded=False):
        try:
            trace = _get(client, f"/v1/traces/{trace_id}")
        except httpx.HTTPError as exc:
            st.error(f"Trace unavailable: {exc}")
            return

        stages = trace.get("stages", [])
        if stages:
            st.markdown(_trace_table(stages), unsafe_allow_html=True)
        metadata = trace.get("metadata") or {}
        latency = trace.get("latency_ms")
        latency_text = f"{float(latency) / 1000:.2f}s" if latency is not None else "—"
        cost_basis = metadata.get("cost_basis", "unknown")
        trace_cost = _escape(_cost(trace.get("cost_usd")))
        st.markdown(
            '<div class="result-meta">'
            f'<div class="meta-item"><strong>Trace cost</strong> {trace_cost}</div>'
            f'<div class="meta-item"><strong>Total latency</strong> {_escape(latency_text)}</div>'
            f'<div class="meta-item"><strong>Accounting</strong> {_escape(cost_basis)}</div>'
            f'<div class="meta-item"><strong>Trace</strong> {_escape(trace_id)}</div>'
            "</div>",
            unsafe_allow_html=True,
        )


def _render_claim_rows(st: Any, claims: list[dict[str, Any]]) -> None:
    for index, claim in enumerate(claims, start=1):
        supported = bool(claim.get("supported")) and bool(claim.get("included", True))
        status = "Supported" if supported else "Needs review"
        row_class = "claim-row" if supported else "claim-row is-unverified"
        status_class = "claim-status" if supported else "claim-status is-unverified"
        claim_id = claim.get("claim_id") or str(index)
        st.markdown(
            f'<div class="{row_class}">'
            f'<div class="{status_class}">Claim { _escape(claim_id) } · {status}</div>'
            f'<div class="claim-text">{_escape(claim.get("text"))}</div>'
            "</div>",
            unsafe_allow_html=True,
        )


def _render_claims(st: Any, claims: list[dict[str, Any]], generation_mode: str) -> None:
    if not claims:
        return
    supported_count = sum(
        bool(claim.get("supported")) and bool(claim.get("included", True)) for claim in claims
    )
    st.markdown(
        '<div class="evidence-label">Claim support</div>',
        unsafe_allow_html=True,
    )
    if generation_mode == "verified":
        st.markdown(
            '<div class="support-summary">'
            f"<strong>{supported_count}/{len(claims)}</strong> claims supported"
            "</div>",
            unsafe_allow_html=True,
        )
        _render_claim_rows(st, claims)
    elif generation_mode == "extractive":
        st.markdown(
            '<div class="support-summary">'
            "<strong>Local evidence</strong> claim scoring is not applied in extractive mode"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="support-summary">'
            "<strong>Unverified answer</strong> claim verification was not applied"
            "</div>",
            unsafe_allow_html=True,
        )


def _render_result(st: Any, client: httpx.Client, search_mode: str, result: dict[str, Any]) -> None:
    is_hybrid = search_mode == "hybrid"
    title = "Full hybrid answer" if is_hybrid else "Keyword-only comparison"
    version = result.get("answered_version") or "No version selected"
    if result.get("abstained"):
        badge = '<span class="result-badge is-muted">No grounded answer</span>'
    else:
        badge = '<span class="result-badge">Evidence found</span>'
    mode_badge = (
        f'<span class="mode-badge">{_escape(result.get("generation_mode", "unknown"))}</span>'
    )
    confidence = f'{float(result.get("confidence", 0) or 0):.2f}'
    with st.container(border=True):
        st.markdown(
            '<div class="result-topline">'
            f'<div class="result-title">{_escape(title)}</div>'
            f'<div>{mode_badge} {badge}</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        if result.get("abstained"):
            st.markdown(
                '<div class="empty-state">'
                "No reliable passage matched this wording. Try a PostgreSQL term such as "
                "<strong>DROP DATABASE</strong>, choose a product version, or use the full "
                "hybrid search."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            answer = str(result.get("answer") or "No answer returned.")
            st.markdown('<div class="answer-label">Answer</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="answer-copy">{_answer_html(answer)}</div>',
                unsafe_allow_html=True,
            )

        matches_count = len(result.get("matches", []))
        citations_count = len(result.get("citations", []))
        st.markdown(
            '<div class="result-meta">'
            f'<div class="meta-item"><strong>Version</strong> {_escape(version)}</div>'
            f'<div class="meta-item"><strong>Confidence</strong> {_escape(confidence)}</div>'
            f'<div class="meta-item"><strong>Matches</strong> {_escape(matches_count)}</div>'
            f'<div class="meta-item"><strong>Citations</strong> {_escape(citations_count)}</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        claims = result.get("claims", [])
        citations = result.get("citations", [])
        generation_mode = str(result.get("generation_mode", "verified"))
        _render_claims(st, claims, generation_mode)
        if citations:
            with st.expander(
                f"Supporting evidence · {len(citations)} passages", expanded=True
            ):
                for number, citation in enumerate(citations, start=1):
                    _render_citation(st, citation, number)
        elif result.get("abstained"):
            st.caption("No citation was attached because the answer was intentionally withheld.")

        trace_id = result.get("trace_id")
        if trace_id:
            _render_trace(st, client, trace_id)


def main() -> None:
    try:
        import streamlit as st
    except ImportError as exc:
        raise RuntimeError(
            "The UI requires the optional 'ui' dependency: pip install -e '.[ui]'"
        ) from exc

    st.set_page_config(
        page_title="Evidence RAG · Query workspace",
        page_icon="⌁",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(f"<style>{_load_styles()}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="brand-mark">Evidence RAG</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="brand-subtitle">'
            "A query workspace for versioned PostgreSQL evidence."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-heading">Access profile</div>', unsafe_allow_html=True)
        preset = st.selectbox(
            "Who are you?",
            ("public reader", "operations reader", "admin"),
            label_visibility="collapsed",
        )
        presets = {
            "public reader": ("demo-public", [], ["reader"]),
            "operations reader": ("demo-operator", ["operations"], ["reader"]),
            "admin": ("demo-admin", ["operations"], ["admin", "reader"]),
        }
        principal, groups, roles = presets[preset]
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("Connection settings", expanded=False):
            api_url = st.text_input(
                "API URL",
                os.getenv("RAG_UI_API_URL", "http://127.0.0.1:8000"),
            )
            secret = st.text_input(
                "Local JWT secret",
                os.getenv("RAG_JWT_SECRET", ""),
                type="password",
            )

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-heading">How this works</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="sidebar-copy">'
            "Hybrid search finds relevant passages. Verified mode asks DeepSeek to answer only "
            "from "
            "public evidence, then checks every claim against its citations."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if not secret:
        st.warning("Set the local JWT secret in Connection settings before querying the API.")
        st.stop()

    token = _token(secret, principal, groups, roles)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        with httpx.Client(base_url=api_url.rstrip("/"), headers=headers, timeout=15.0) as client:
            coverage = _get(client, "/v1/corpus/coverage")
            summary = _get(client, "/v1/traces/summary")
    except httpx.HTTPError as exc:
        st.markdown(
            '<div class="masthead"><div><h1 class="masthead-title">Evidence RAG</h1>'
            '<div class="masthead-copy">Evidence-first search for PostgreSQL documentation.</div>'
            "</div></div>",
            unsafe_allow_html=True,
        )
        st.error(f"The API is unavailable. Check Connection settings, then retry. ({exc})")
        st.stop()

    st.markdown(
        '<div class="masthead">'
        '<div><h1 class="masthead-title">Ask with evidence attached.</h1>'
        '<div class="masthead-copy">'
        "Search PostgreSQL documentation across versions. Every answer keeps its "
        "version, claims, quotes, and cost visible."
        "</div>"
        "</div>"
        '<span class="connection-badge">Corpus online</span>'
        "</div>",
        unsafe_allow_html=True,
    )

    total_chunks = int(coverage.get("total_active_chunks", 0))
    linked_chunks = int(coverage.get("vector_linked_chunks", 0))
    embeddings = int(coverage.get("embedding_records", 0))
    missing = int(coverage.get("missing_dense_chunks", 0))
    vector_percent = (linked_chunks / total_chunks * 100) if total_chunks else 0
    st.markdown('<div class="section-heading">Corpus at a glance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">The searchable collection behind your next answer.</div>',
        unsafe_allow_html=True,
    )
    metric_columns = st.columns(4, gap="medium")
    metrics = (
        ("Indexed chunks", f"{total_chunks:,}", "active PostgreSQL passages"),
        ("Vector coverage", f"{vector_percent:.0f}%", f"{linked_chunks:,} linked passages"),
        ("Unique embeddings", f"{embeddings:,}", "BGE-small vectors"),
        ("Query spend", _cost(summary.get("cost_usd")), "recorded provider usage"),
    )
    for column, (label, value, detail) in zip(metric_columns, metrics, strict=True):
        with column:
            st.markdown(_metric_card(label, value, detail), unsafe_allow_html=True)

    if missing:
        status_message = (
            f"{missing:,} indexed passages do not have a verified dense vector. "
            "Keyword search remains available."
        )
        st.markdown(
            f'<div class="status-note">{_escape(status_message)}</div>',
            unsafe_allow_html=True,
        )
    else:
        status_message = (
            "All indexed passages have verified dense vectors. Hybrid search can use both "
            "meaning and exact PostgreSQL terms."
        )
        st.markdown(
            f'<div class="status-note">{_escape(status_message)}</div>',
            unsafe_allow_html=True,
        )

    ask_copy = (
        "Use the language from PostgreSQL documentation when possible. Choose a version "
        "when the answer can differ between releases."
    )
    with st.container(border=True):
        st.markdown(
            '<div class="ask-panel-title">Ask the corpus</div>'
            f'<div class="ask-panel-copy">{_escape(ask_copy)}</div>',
            unsafe_allow_html=True,
        )
        query = st.text_area(
            "Question",
            DEFAULT_QUERY,
            height=84,
            help="Example: How do I drop a PostgreSQL database in PostgreSQL 17?",
        )
        controls = st.columns(3, gap="medium")
        with controls[0]:
            version = st.selectbox(
                "Product version",
                ("auto", "pg-15", "pg-16", "pg-17"),
                help=(
                    "Auto lets retrieval select the best supported version. "
                    "Pick one when version matters."
                ),
            )
        with controls[1]:
            mode = st.selectbox(
                "Answer mode",
                ("verified", "extractive", "unverified"),
                help="Verified uses DeepSeek and checks claims. Extractive is local and free.",
            )
        with controls[2]:
            compare = st.checkbox(
                "Show keyword-only comparison",
                value=False,
                help=(
                    "Runs an additional sparse-only search so you can see what hybrid "
                    "retrieval recovers."
                ),
            )
        st.caption(
            "Verified answers may incur provider usage. "
            "Extractive answers stay local and cost $0."
        )
        ask = st.button("Find an answer", type="primary", width="stretch")

    if not ask or not query.strip():
        return

    payload_base: dict[str, Any] = {
        "query": query,
        "generation_mode": mode,
        "product_version": None if version == "auto" else version,
        "version_mode": "none" if version == "auto" else "explicit",
        "top_k": 5,
        "candidate_k": 30,
    }
    search_modes = ["hybrid"] + (["sparse"] if compare else [])
    results: list[tuple[str, dict[str, Any]]] = []
    errors: list[str] = []
    with st.spinner("Searching the indexed evidence…"):
        with httpx.Client(base_url=api_url.rstrip("/"), headers=headers, timeout=90.0) as client:
            for search_mode in search_modes:
                try:
                    payload = {**payload_base, "search_mode": search_mode}
                    result = _post(client, "/v1/query", payload)
                    results.append((search_mode, result))
                except httpx.HTTPError as exc:
                    errors.append(f"{search_mode}: {exc}")
            st.markdown(
                '<div class="results-header"><div class="results-title">Answer</div>'
                '<div class="results-copy">'
                "Read the answer first. Open evidence and diagnostics when you need "
                "to audit it."
                "</div></div>",
                unsafe_allow_html=True,
            )
            for search_mode, result in results:
                _render_result(st, client, search_mode, result)
            if compare and len(results) == 2:
                hybrid_result = next(item for mode_name, item in results if mode_name == "hybrid")
                sparse_result = next(item for mode_name, item in results if mode_name == "sparse")
                if not hybrid_result.get("abstained") and sparse_result.get("abstained"):
                    st.info(
                        "Hybrid retrieval found grounded evidence that keyword-only search missed. "
                        "This is why the full hybrid answer is the default."
                    )
    for error in errors:
        st.error(f"Query failed: {error}")


if __name__ == "__main__":
    main()
