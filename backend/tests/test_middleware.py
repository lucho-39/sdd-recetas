"""Unit tests for the observability middleware (rate limit / maintenance / errors)."""
import pytest
from starlette.requests import Request
from starlette.responses import Response

import app.main as main_module
from app.core.app_settings import _cache


def _request(path: str = "/api/v1/boom", method: str = "GET") -> Request:
    return Request(
        {
            "type": "http",
            "path": path,
            "method": method,
            "headers": [],
            "query_string": b"",
            "client": ("1.2.3.4", 1234),
        }
    )


async def test_middleware_records_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple] = []

    async def fake_record(path, method, status_code, message):
        calls.append((path, status_code))

    monkeypatch.setattr(main_module, "_record_error", fake_record)
    _cache["value"] = None  # defaults: no maintenance, no rate limit

    async def call_next(_request):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await main_module.observability_middleware(_request(), call_next)

    assert calls == [("/api/v1/boom", 500)]


async def test_middleware_records_5xx_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple] = []

    async def fake_record(path, method, status_code, message):
        calls.append((path, status_code))

    monkeypatch.setattr(main_module, "_record_error", fake_record)
    _cache["value"] = None

    async def call_next(_request):
        return Response(status_code=502)

    response = await main_module.observability_middleware(_request(), call_next)
    assert response.status_code == 502
    assert calls == [("/api/v1/boom", 502)]


async def test_middleware_maintenance_blocks_public() -> None:
    _cache["value"] = {"maintenance_mode": True, "rate_limit_per_minute": 0}

    async def call_next(_request):
        return Response(status_code=200)

    blocked = await main_module.observability_middleware(_request("/api/v1/recipes"), call_next)
    assert blocked.status_code == 503

    allowed = await main_module.observability_middleware(
        _request("/api/admin/metrics"), call_next
    )
    assert allowed.status_code == 200


def _request_with_forwarded(path: str, forwarded_for: str) -> Request:
    # Same proxy peer as _request would use, different forwarded client.
    return Request(
        {
            "type": "http",
            "path": path,
            "method": "GET",
            "headers": [(b"x-forwarded-for", forwarded_for.encode())],
            "query_string": b"",
            "client": ("10.0.0.1", 1234),
        }
    )


async def test_middleware_rate_limit_keys_by_forwarded_client() -> None:
    """Behind Caddy the socket peer is always the proxy: two users behind it
    must not share one bucket, and one user must still hit the limit."""
    main_module._rate_buckets.clear()
    _cache["value"] = {"maintenance_mode": False, "rate_limit_per_minute": 2}

    async def call_next(_request):
        return Response(status_code=200)

    first = _request_with_forwarded("/api/v1/recipes", "9.9.9.9")
    assert (await main_module.observability_middleware(first, call_next)).status_code == 200
    assert (await main_module.observability_middleware(first, call_next)).status_code == 200

    # Same proxy peer, different forwarded client: fresh bucket, allowed.
    other = _request_with_forwarded("/api/v1/recipes", "8.8.8.8")
    assert (await main_module.observability_middleware(other, call_next)).status_code == 200

    # Same forwarded client a third time: over the limit.
    again = _request_with_forwarded("/api/v1/recipes", "9.9.9.9")
    assert (await main_module.observability_middleware(again, call_next)).status_code == 429
