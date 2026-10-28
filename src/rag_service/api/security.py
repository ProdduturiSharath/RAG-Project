"""Authentication and bounded request controls for the public API."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import jwt
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from rag_service.settings import Settings


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    """Identity material accepted only after signature and claim validation."""

    principal: str
    groups: tuple[str, ...] = ()
    roles: tuple[str, ...] = ()

    def can_mutate(self) -> bool:
        return bool(set(self.roles).intersection({"admin", "ingest", "ingestion"}))


class JWTVerifier:
    """Strict HS256 verifier; caller identity never comes from request JSON."""

    def __init__(self, settings: Settings) -> None:
        self.secret = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        if self.algorithm != "HS256":
            raise ValueError("only HS256 is enabled for the local JWT boundary")
        if len(self.secret.encode("utf-8")) < 32:
            raise ValueError("JWT secret must be at least 32 UTF-8 bytes")

    def verify(self, token: str) -> AuthenticatedPrincipal:
        if not token or any(character.isspace() for character in token):
            raise ValueError("malformed bearer token")
        try:
            claims = jwt.decode(
                token,
                self.secret,
                algorithms=["HS256"],
                options={"require": ["exp", "iat", "sub"], "verify_aud": False},
            )
        except jwt.PyJWTError as exc:
            raise ValueError("invalid bearer token") from exc
        if not isinstance(claims, Mapping):
            raise ValueError("invalid JWT claims")
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("JWT sub must be a non-empty string")
        groups = _claim_values(claims.get("groups"), "groups")
        roles = list(_claim_values(claims.get("roles"), "roles"))
        roles.extend(_claim_values(claims.get("scope"), "scope", split_string=True))
        return AuthenticatedPrincipal(
            principal=subject,
            groups=tuple(dict.fromkeys(groups)),
            roles=tuple(dict.fromkeys(roles)),
        )

    def verify_request(self, request: Request) -> AuthenticatedPrincipal:
        value = request.headers.get("authorization", "")
        scheme, separator, token = value.partition(" ")
        if scheme.casefold() != "bearer" or not separator or not token:
            raise HTTPException(status_code=401, detail="authentication required")
        try:
            return self.verify(token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="invalid authentication token") from exc


def _claim_values(value: Any, name: str, *, split_string: bool = False) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        values: Iterable[Any] = value.split() if split_string else (value,)
    elif isinstance(value, list):
        values = value
    else:
        raise ValueError(f"JWT {name} must be a string or string list")
    raw_values = list(values)
    result = tuple(item for item in raw_values if isinstance(item, str) and item.strip())
    if len(result) != len(raw_values):
        raise ValueError(f"JWT {name} must contain only strings")
    return result


class RateLimiter:
    """Small process-local sliding-window limiter for one API worker."""

    def __init__(self, limit: int, window_seconds: float) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._events: defaultdict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> float | None:
        now = time.monotonic()
        async with self._lock:
            events = self._events[key]
            while events and events[0] <= now - self.window_seconds:
                events.popleft()
            if len(events) >= self.limit:
                return max(1.0, events[0] + self.window_seconds - now)
            events.append(now)
            return None


def client_key(request: Request, verifier: JWTVerifier) -> str:
    header = request.headers.get("authorization", "")
    _, separator, token = header.partition(" ")
    if separator and token:
        try:
            return "principal:" + verifier.verify(token).principal
        except ValueError:
            pass
    return "ip:" + (request.client.host if request.client else "unknown")


def enforce_payload_limits(payload: Any, settings: Settings) -> None:
    """Apply configurable structural limits after Pydantic type validation."""
    if hasattr(payload, "query") and len(payload.query) > settings.max_query_chars:
        raise HTTPException(status_code=413, detail="query exceeds configured length limit")
    sections = getattr(payload, "sections", ())
    if len(sections) > settings.max_sections:
        raise HTTPException(status_code=413, detail="too many sections")
    document_text = getattr(payload, "text", None) or ""
    if len(document_text) > settings.max_document_chars:
        raise HTTPException(status_code=413, detail="document exceeds configured length limit")
    total_section_text = 0
    for section in sections:
        if len(section.text) > settings.max_section_chars:
            raise HTTPException(status_code=413, detail="section exceeds configured length limit")
        total_section_text += len(section.text)
    if total_section_text > settings.max_document_chars:
        raise HTTPException(
            status_code=413, detail="document sections exceed configured length limit"
        )
    metadata = _metadata_values(payload)
    key_count = 0
    for value in metadata:
        keys, depth = _metadata_shape(value)
        key_count += keys
        if depth > settings.max_metadata_depth:
            raise HTTPException(status_code=413, detail="metadata nesting exceeds configured limit")
    if key_count > settings.max_metadata_keys:
        raise HTTPException(status_code=413, detail="too many metadata keys")


def _metadata_values(payload: Any) -> tuple[Any, ...]:
    values: list[Any] = []
    for name in ("metadata", "page_metadata", "source", "access_policy"):
        value = getattr(payload, name, None)
        if value is not None:
            values.append(value.model_dump() if hasattr(value, "model_dump") else value)
    for section in getattr(payload, "sections", ()):
        for name in ("metadata", "page_metadata"):
            values.append(getattr(section, name, {}))
    return tuple(values)


def _metadata_shape(value: Any, depth: int = 1) -> tuple[int, int]:
    if isinstance(value, list):
        keys = 0
        deepest = depth
        for nested in value:
            child_keys, child_depth = _metadata_shape(nested, depth + 1)
            keys += child_keys
            deepest = max(deepest, child_depth)
        return keys, deepest
    if not isinstance(value, Mapping):
        return 0, depth
    keys = len(value)
    deepest = depth
    for nested in value.values():
        child_keys, child_depth = _metadata_shape(nested, depth + 1)
        keys += child_keys
        deepest = max(deepest, child_depth)
    return keys, deepest


async def bounded_call_next(request: Request, call_next: Any, timeout_seconds: float) -> Any:
    try:
        return await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
    except TimeoutError:
        return JSONResponse(status_code=504, content={"detail": "request timed out"})


async def security_middleware(request: Request, call_next: Any) -> Any:
    settings: Settings = request.app.state.settings
    if request.url.path not in {"/health", "/v1/health"}:
        content_length = request.headers.get("content-length")
        try:
            declared_length = int(content_length) if content_length else 0
        except ValueError:
            return JSONResponse(status_code=422, content={"detail": "invalid content length"})
        if declared_length > settings.max_request_body_bytes:
            return JSONResponse(status_code=413, content={"detail": "request body too large"})
        body = await request.body()
        if len(body) > settings.max_request_body_bytes:
            return JSONResponse(status_code=413, content={"detail": "request body too large"})
        retry_after = await request.app.state.rate_limiter.check(
            client_key(request, request.app.state.jwt_verifier)
        )
        if retry_after is not None:
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers={"Retry-After": str(int(retry_after))},
            )
    return await bounded_call_next(request, call_next, settings.request_timeout_seconds)


__all__ = [
    "AuthenticatedPrincipal",
    "JWTVerifier",
    "RateLimiter",
    "client_key",
    "enforce_payload_limits",
    "security_middleware",
]
