"""Smoke test for Monkey Paw runtime health.

Purpose: Prove real runtime health of your app (v4 or v5) and pinpoint what's broken.
- Auto-locates your FastAPI app via env (MONKEYPAW_APP_FILE/MODULE) or common paths.
- Hits /health and /healthz for real using TestClient.
- Checks key deps (free), your ChatGPT Desktop bridge shim, and voice/redis/pg flags.
- Exits non-zero on failure so you know it's not "pretend working".
"""
from __future__ import annotations

import importlib
import importlib.util
import json
import os
import sys
from pathlib import Path

CANDIDATES = ("monkeypaw.api.app", "app.api.app", "app")  # module:attr=app


def _load_from_module(module_name: str, attr: str):
    mod = importlib.import_module(module_name)
    return getattr(mod, attr, None)


def _load_from_file(file_path: str, attr: str):
    path = Path(file_path).expanduser().resolve()
    spec = importlib.util.spec_from_file_location("_mp_app_mod", str(path))
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return getattr(mod, attr, None)


def resolve_app():
    attr = os.environ.get("MONKEYPAW_APP_ATTR", "app")
    f = os.environ.get("MONKEYPAW_APP_FILE")
    m = os.environ.get("MONKEYPAW_APP_MODULE")
    if f:
        return _load_from_file(f, attr), f":file:{f}:{attr}"
    if m:
        return _load_from_module(m, attr), f":module:{m}:{attr}"
    for mod in CANDIDATES:
        try:
            return _load_from_module(mod, attr), f":module:{mod}:{attr}"
        except Exception:
            continue
    raise RuntimeError("No app found (set MONKEYPAW_APP_FILE or MONKEYPAW_APP_MODULE).")


def dep_ok(name: str) -> tuple[bool, str | None]:
    try:
        importlib.import_module(name)
        return True, None
    except Exception as e:
        return False, str(e)


def main() -> None:
    out: dict = {"ok": False}
    try:
        app, where = resolve_app()
        out["where"] = where
    except Exception as e:
        out["error"] = f"resolve_app: {e}"
        print(json.dumps(out, indent=2))
        sys.exit(2)

    # Is it FastAPI?
    try:
        from fastapi import FastAPI

        is_fastapi = isinstance(app, FastAPI)
    except Exception:
        is_fastapi = False
    out["is_fastapi"] = is_fastapi
    if not is_fastapi:
        out["error"] = "Resolved object is not FastAPI `app`"
        print(json.dumps(out, indent=2))
        sys.exit(2)

    # Route list + live /health tests
    try:
        from starlette.testclient import TestClient

        routes = sorted({r.path for r in app.router.routes})
        out["routes"] = routes
        missing = [p for p in ("/health", "/healthz") if p not in routes]
        out["missing_health_routes"] = missing
        with TestClient(app) as client:
            r1 = client.get("/health")
            r2 = client.get("/healthz")
        out["health_results"] = {
            "/health": {"code": r1.status_code, "body": r1.text},
            "/healthz": {"code": r2.status_code, "body": r2.text},
        }
    except Exception as e:
        out["error"] = f"health_check: {e}"
        print(json.dumps(out, indent=2))
        sys.exit(2)

    # Dependencies you care about (all free/optional)
    deps = {}
    for name in [
        "fastapi",
        "uvicorn",
        "pydantic",
        "httpx",
        "starlette",
        "redis",
        "psycopg2",
        "edge_tts",
        "TTS",
        "piper",
    ]:
        ok, err = dep_ok(name)
        deps[name] = {"ok": ok, "detail": err}
    out["deps"] = deps

    # Desktop bridge presence (optional): don't fail if missing
    try:
        from app.utils import chatgpt_desktop as _cd  # your existing shim

        bridge = hasattr(_cd, "_CLIENT") and hasattr(_cd._CLIENT, "send_message")
    except Exception:
        bridge = False
    out["chatgpt_desktop_bridge"] = bridge

    # Env feature flags you already use (kept free/optional)
    out["features"] = {
        "FEATURE_REDIS": os.environ.get("FEATURE_REDIS", "0"),
        "FEATURE_PG": os.environ.get("FEATURE_PG", "0"),
        "FEATURE_CHATGPT_DESKTOP": os.environ.get("FEATURE_CHATGPT_DESKTOP", "1"),
    }

    # Decide pass/fail
    health_ok = (
        out["health_results"]["/health"]["code"] == 200
        and out["health_results"]["/healthz"]["code"] == 200
    )
    out["ok"] = bool(health_ok)
    print(json.dumps(out, indent=2))
    sys.exit(0 if health_ok else 3)


if __name__ == "__main__":
    main()
