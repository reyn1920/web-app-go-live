from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


def _import_app():
    for mod in ("backend.app", "app", "backend.main", "main"):
        try:
            m = importlib.import_module(mod)
        except ImportError:
            continue
        if hasattr(m, "app"):
            return m
    return None


app_module = _import_app()
if app_module is None:
    pytest.skip("Could not import FastAPI app from backend.app/app/main", allow_module_level=True)

app = app_module.app
client = TestClient(app)


def _candidate_health_paths() -> list[str]:
    # Common health/status endpoints used across FastAPI projects
    return [
        "/health",
        "/healthz",
        "/status",
        "/api/health",
        "/api/status",
        "/__health",
    ]


def test_health_endpoint_exists_or_skip() -> None:
    schema = app.openapi()
    paths = set(schema.get("paths", {}).keys())
    candidates = [p for p in _candidate_health_paths() if p in paths]
    if not candidates:
        pytest.skip("No standard health endpoint found in OpenAPI schema.")
    # choose the first one and ping it
    target = candidates[0]
    r = client.get(target)
    assert r.status_code < 500
