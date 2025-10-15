"""Universal dev server for Monkey Paw that auto-discovers FastAPI app."""
from __future__ import annotations

import importlib
import logging
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

log = logging.getLogger("devserver")

# Candidate locations for your FastAPI `app` object.
_CANDIDATES = [
    ("monkeypaw.api.app", "app"),  # v5-style
    ("app.api.app", "app"),        # v4-style
    ("app", "app"),                # single-file root app.py
]


def _import_app(module_name: str, attr: str) -> Optional[FastAPI]:
    try:
        mod = importlib.import_module(module_name)
    except (ImportError, AttributeError, TypeError) as e:
        log.debug("Import miss: %s (%s)", module_name, e)
        return None
    found_app = getattr(mod, attr, None)
    if found_app is None or not isinstance(found_app, FastAPI):
        log.debug("No FastAPI `app` at %s:%s", module_name, attr)
        return None
    return found_app


def _ensure_health_once(fastapi_app: FastAPI) -> None:
    """Add /health and /healthz only if not already present."""
    existing = {route.path for route in fastapi_app.router.routes}
    if "/health" not in existing:

        @fastapi_app.get("/health")
        def _health() -> JSONResponse:  # type: ignore[func-returns-value]
            return JSONResponse({"status": "ok"})

    if "/healthz" not in existing:

        @fastapi_app.get("/healthz")
        def _healthz() -> JSONResponse:  # type: ignore[func-returns-value]
            return JSONResponse({"status": "ok"})


def _pick_app() -> FastAPI:
    """Find an existing app or provide a minimal fallback with health."""
    env_mod = os.environ.get("MONKEYPAW_APP_MODULE")
    env_attr = os.environ.get("MONKEYPAW_APP_ATTR", "app")
    if env_mod:
        found = _import_app(env_mod, env_attr)
        if found:
            _ensure_health_once(found)
            log.info("Using app from env: %s:%s", env_mod, env_attr)
            return found
        log.warning("Env override failed to load %s:%s", env_mod, env_attr)
    for mod, attr in _CANDIDATES:
        found = _import_app(mod, attr)
        if found:
            _ensure_health_once(found)
            log.info("Using discovered app: %s:%s", mod, attr)
            return found
    log.warning("No FastAPI app found; serving health-only fallback.")
    fallback = FastAPI(title="Monkey Paw (fallback)")
    _ensure_health_once(fallback)
    return fallback


app: FastAPI = _pick_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("devserver:app", host="127.0.0.1", port=8789, reload=True)
