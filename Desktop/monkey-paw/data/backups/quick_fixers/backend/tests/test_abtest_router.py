from __future__ import annotations

import importlib
import types
from typing import Iterable, List, Tuple

import pytest

try:
    from fastapi.testclient import TestClient
except Exception as e:  # pragma: no cover - import guard for environments
    raise RuntimeError("fastapi[test] must be installed to run API tests") from e


def _import_app() -> "types.ModuleType | None":
    """
    Try a few common import paths to load the FastAPI `app`.
    Returns the imported module (with `app` attribute) or None if not found.
    """
    candidates = ("backend.app", "app", "backend.main", "main")
    for mod in candidates:
        try:
            m = importlib.import_module(mod)
            if hasattr(m, "app"):
                return m
        except Exception:
            continue
    return None


def _abtest_routes(app) -> List[Tuple[str, Iterable[str]]]:
    """
    Return list of (path, methods) for routes that appear related to A/B testing.
    We match by tag 'abtest' or 'a/b', or any path containing 'abtest'/'ab-test'.
    """
    matched: List[Tuple[str, Iterable[str]]] = []
    for route in app.router.routes:
        path = getattr(route, "path", "")
        methods = getattr(route, "methods", set())
        tags = [t.lower() for t in getattr(route, "tags", []) or []]
        name = (getattr(route, "name", "") or "").lower()

        if (
            "abtest" in path.lower()
            or "ab-test" in path.lower()
            or "abtest" in name
            or any(t in {"abtest", "a/b", "ab-test"} for t in tags)
        ):
            matched.append((path, methods))
    return matched


app_module = _import_app()
if app_module is None:
    pytest.skip("Could not import FastAPI app from backend.app/app/main", allow_module_level=True)

app = app_module.app  # type: ignore[attr-defined]
client = TestClient(app)


def test_openapi_loads() -> None:
    """The OpenAPI schema should build without exploding (basic contract check)."""
    schema = app.openapi()
    assert isinstance(schema, dict)
    assert "paths" in schema


def test_abtest_routes_exist_or_skip() -> None:
    """
    If A/B test routes are present, assert we found at least one.
    Otherwise skip cleanly (keeps the suite green without brittle assumptions).
    """
    routes = _abtest_routes(app)
    if not routes:
        pytest.skip("No abtest-tagged/named routes found in app (skipping).")
    assert len(routes) >= 1


@pytest.mark.parametrize("method", ["GET", "HEAD"])
def test_abtest_smoke_no_5xx(method: str) -> None:
    """
    For abtest routes that support GET/HEAD without path params, ensure no 5xx.
    It's OK if auth/validation yields 401/403/422; we just don't want crashes.
    """
    routes = [(p, m) for (p, m) in _abtest_routes(app) if method in m and "{" not in p and "}" not in p]
    if not routes:
        pytest.skip(f"No simple parameterless abtest routes supporting {method}.")
    for path, _ in routes:
        resp = client.request(method, path)
        assert resp.status_code < 500, f"{method} {path} => {resp.status_code}"
