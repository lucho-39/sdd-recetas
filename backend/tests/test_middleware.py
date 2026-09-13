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

    async def fake_record(path, method, status_code, message):  # noqa: ANN001
        calls.append((path, status_code))

    monkeypatch.setattr(main_module, "_record_error", fake_record)
    _cache["value"] = None  # defaults: no maintenance, no rate limit

    async def call_next(_request):  # noqa: ANN001
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await main_module.observability_middleware(_request(), call_next)

    assert calls == [("/api/v1/boom", 500)]


async def test_middleware_records_5xx_responses(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple] = []

    async def fake_record(path, method, status_code, message):  # noqa: ANN001
        calls.append((path, status_code))

    monkeypatch.setattr(main_module, "_record_error", fake_record)
    _cache["value"] = None

    async def call_next(_request):  # noqa: ANN001
        return Response(status_code=502)

    response = await main_module.observability_middleware(_request(), call_next)
    assert response.status_code == 502
    assert calls == [("/api/v1/boom", 502)]


async def test_middleware_maintenance_blocks_public() -> None:
    _cache["value"] = {"maintenance_mode": True, "rate_limit_per_minute": 0}

    async def call_next(_request):  # noqa: ANN001
        return Response(status_code=200)

    blocked = await main_module.observability_middleware(_request("/api/v1/recipes"), call_next)
    assert blocked.status_code == 503

    allowed = await main_module.observability_middleware(
        _request("/api/admin/metrics"), call_next
    )
    assert allowed.status_code == 200
