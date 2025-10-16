"""V5-only dev server that auto-discovers FastAPI app (handles spaces/dashes)."""
from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import traceback
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse

log = logging.getLogger("devserver_v5")

# You can force an exact file with:  export V5_APP_FILE="/abs/path/to/app.py"
# Or force a module with:           export V5_APP_MODULE="monkeypaw.api.app"
# Optional attr (defaults to 'app'): export V5_APP_ATTR="app"

_CANDIDATES = [
    # common v5 layouts:
    ("monkeypaw.api.app", "app"),
    ("app.api.app", "app"),
    ("app", "app"),
]


def _import_app_from_file(file_path: str, attr: str) -> FastAPI | None:
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        log.error("V5_APP_FILE not found: %s", path)
        return None
    spec = importlib.util.spec_from_file_location("_v5_app_mod", str(path))
    if not spec or not spec.loader:
        log.error("Cannot load spec for %s", path)
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    except Exception as e:
        log.error("Import error in %s: %s", path, e)
        log.debug("%s", traceback.format_exc())
        return None
    obj = getattr(mod, attr, None)
    if isinstance(obj, FastAPI):
        return obj
    log.error(
        "Attr %r on %s is not FastAPI (got: %r)",
        attr,
        path,
        type(obj).__name__ if obj else None,
    )
    return None


def _import_app_from_module(module_name: str, attr: str) -> FastAPI | None:
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        log.debug("Module import miss: %s (%s)", module_name, e)
        return None
    obj = getattr(mod, attr, None)
    if isinstance(obj, FastAPI):
        return obj
    return None


def _ensure_health_once(fastapi_app: FastAPI) -> None:
    """Add /health and /healthz only if not already present (non-destructive)."""
    paths = {r.path for r in fastapi_app.router.routes}
    if "/health" not in paths:

        @fastapi_app.get("/health")
        def _health() -> JSONResponse:  # type: ignore[func-returns-value]
            return JSONResponse({"status": "ok"})

    if "/healthz" not in paths:

        @fastapi_app.get("/healthz")
        def _healthz() -> JSONResponse:  # type: ignore[func-returns-value]
            return JSONResponse({"status": "ok"})


def _ensure_ops_status(fastapi_app: FastAPI) -> None:
    """Add /_ops/status and /version (non-destructive) for quick runtime checks."""
    paths = {r.path for r in fastapi_app.router.routes}
    if "/_ops/status" not in paths:

        @fastapi_app.get("/_ops/status")
        def _ops_status() -> JSONResponse:  # type: ignore[func-returns-value]
            routes = sorted({r.path for r in fastapi_app.router.routes})
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

    if "/version" not in paths:

        @fastapi_app.get("/version")
        def _version() -> PlainTextResponse:  # type: ignore[func-returns-value]
            return PlainTextResponse("v5-devserver")


def _pick_app_v5() -> FastAPI:
    attr = os.environ.get("V5_APP_ATTR", "app")
    f = os.environ.get("V5_APP_FILE")
    m = os.environ.get("V5_APP_MODULE")

    if f:
        found = _import_app_from_file(f, attr)
        if found:
            _ensure_health_once(found)
            _ensure_ops_status(found)
            log.info("Using v5 app from file: %s (attr=%s)", f, attr)
            return found
        log.error("File override FAILED for %s (attr=%s). See errors above.", f, attr)

    if m:
        found = _import_app_from_module(m, attr)
        if found:
            _ensure_health_once(found)
            _ensure_ops_status(found)
            log.info("Using v5 app from module: %s:%s", m, attr)
            return found
        log.error("Module override FAILED for %s:%s.", m, attr)

    # Try common module locations inside v5
    for mod, at in _CANDIDATES:
        found = _import_app_from_module(mod, at)
        if found:
            _ensure_health_once(found)
            _ensure_ops_status(found)
            log.info("Using discovered v5 app: %s:%s", mod, at)
            return found

    # Fallback (health-only) so curl never 404s while you wire the real app.
    log.warning("No v5 FastAPI app found; serving HEALTH-ONLY FALLBACK.")
    log.warning(
        "Set V5_APP_FILE=/absolute/path/to/app.py or V5_APP_MODULE=package.module "
        "(attr via V5_APP_ATTR)."
    )
    fallback = FastAPI(title="Monkey Paw v5 (fallback)")
    _ensure_health_once(fallback)
    _ensure_ops_status(fallback)
    return fallback


# uvicorn entrypoint:
app: FastAPI = _pick_app_v5()

if __name__ == "__main__":
    import uvicorn

    # Reduce reload flapping from noisy files while you're wiring v5
    uvicorn.run(
        "devserver_v5:app",
        host="127.0.0.1",
        port=8789,
        reload=True,
        reload_excludes=[
            "sitecustomize.py",
            "tools/*",
            ".lint_backups/*",
            "monkeypaw-v5/tools/*",
        ],
    )
