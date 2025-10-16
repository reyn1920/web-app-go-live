"""Universal dev server for Monkey Paw that auto-discovers FastAPI app."""
from __future__ import annotations

import importlib
import importlib.util
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse

log = logging.getLogger("devserver")

# Candidate locations for your FastAPI `app` object.
_CANDIDATES = [
    ("monkeypaw.api.app", "app"),  # v5-style
    ("app.api.app", "app"),        # v4-style
    ("app", "app"),                # single-file root app.py
]


def _ensure_ops_status(fastapi_app: FastAPI) -> None:
    """Add /_ops/status (non-destructive) so we can quickly verify runtime."""
    paths = {r.path for r in fastapi_app.router.routes}  # type: ignore[attr-defined]
    if "/_ops/status" in paths:
        return

    @fastapi_app.get("/_ops/status")
    def _ops_status() -> JSONResponse:  # type: ignore[func-returns-value]
        try:
            routes = sorted({r.path for r in fastapi_app.router.routes})  # type: ignore[attr-defined]
            return JSONResponse({
                "ok": True,
                "routes": routes,
                "env": {
                    "FEATURE_REDIS": os.environ.get("FEATURE_REDIS", "0"),
                    "FEATURE_PG": os.environ.get("FEATURE_PG", "0"),
                    "FEATURE_CHATGPT_DESKTOP": os.environ.get(
                        "FEATURE_CHATGPT_DESKTOP", "1"
                    ),
                },
            })
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


def _import_app(module_name: str, attr: str) -> FastAPI | None:
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
    existing = {route.path for route in fastapi_app.router.routes}  # type: ignore[attr-defined]
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
    env_file = os.environ.get("MONKEYPAW_APP_FILE")

    # Highest priority: explicit file path (handles spaces/dashes in folders)
    if env_file:
        try:
            spec = importlib.util.spec_from_file_location(
                "_monkeypaw_app_mod", str(Path(env_file).expanduser())
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                obj = getattr(mod, env_attr, None)
                if isinstance(obj, FastAPI):
                    _ensure_health_once(obj)
                    _ensure_ops_status(obj)
                    log.info("Using app from file: %s (attr=%s)", env_file, env_attr)
                    return obj
        except Exception as e:
            log.error("File override FAILED for %s (attr=%s): %s", env_file, env_attr, e)

    if env_mod:
        found = _import_app(env_mod, env_attr)
        if found:
            _ensure_health_once(found)
            _ensure_ops_status(found)
            log.info("Using app from env: %s:%s", env_mod, env_attr)
            return found
        log.warning("Env override failed to load %s:%s", env_mod, env_attr)
    for mod, attr in _CANDIDATES:
        found = _import_app(mod, attr)
        if found:
            _ensure_health_once(found)
            _ensure_ops_status(found)
            log.info("Using discovered app: %s:%s", mod, attr)
            return found
    log.warning("No FastAPI app found; serving health-only fallback.")
    fallback = FastAPI(title="Monkey Paw (fallback)")
    _ensure_health_once(fallback)
    _ensure_ops_status(fallback)
    return fallback


app: FastAPI = _pick_app()

if __name__ == "__main__":
    import uvicorn

    # Stop reload flapping on files that churn (sitecustomize/tools/backups).
    uvicorn.run(
        "devserver:app",
        host="127.0.0.1",
        port=8789,
        reload=True,
        reload_excludes=[
            "sitecustomize.py",
            "tools/*",
            ".lint_backups/*",
        ],
    )
