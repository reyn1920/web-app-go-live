"""JSON logging with request_id, rotation, FastAPI middleware, and uvicorn access parsing (lint-safe)."""

from __future__ import annotations

import json
import logging
import os
import re
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from pythonjsonlogger import jsonlogger  # type: ignore

# A contextvar all formatters/filters can read
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Inject request_id from contextvar into every LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


_ACCESS_RE = re.compile(
    r'(?P<client>[\d\.:]+)\s*-\s*"(?P<method>[A-Z]+)\s+(?P<path>[^"]+?)\s+HTTP/(?P<http>[\d.]+)"\s+(?P<status>\d{3})'
)


class UvicornAccessFilter(logging.Filter):
    """
    Normalize uvicorn.access records into structured fields.
    Works with standard uvicorn message format; degrades gracefully.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name != "uvicorn.access":
            return True

        # Defaults
        client_addr = getattr(record, "client_addr", "")
        method = ""
        path = ""
        http_version = ""
        status_code = getattr(record, "status_code", None)

        # Uvicorn often places the rendered message in getMessage()
        msg = record.getMessage()

        # Try attributes first (some uvicorn versions supply extras)
        request_line = getattr(record, "request_line", "")
        if request_line:
            # Example: 'GET /api/health HTTP/1.1'
            parts = request_line.split()
            if len(parts) >= 3:
                method, path = parts[0], parts[1]
                if parts[2].upper().startswith("HTTP/"):
                    http_version = parts[2].split("/", 1)[-1]

        # If still missing, parse the stringified line
        if not method or not path or not http_version or status_code is None:
            m = _ACCESS_RE.search(msg)
            if m:
                if not client_addr:
                    client_addr = m.group("client")
                method = method or m.group("method")
                path = path or m.group("path")
                http_version = http_version or m.group("http")
                try:
                    status_code = int(m.group("status"))
                except ValueError:
                    # Leave as None; formatter will omit if absent
                    status_code = None

        # Attach normalized fields to record so the JSON formatter can emit them
        record.client_addr = client_addr
        record.method = method
        record.path = path
        record.http_version = http_version
        record.status_code = status_code if status_code is not None else ""

        # Mark record type for downstream queries/dashboards
        record.record_type = "access"
        return True


class UtcJsonFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that forces UTC ISO8601 timestamps and stable key order."""

    def process_log_record(self, log_record: Dict[str, Any]) -> Dict[str, Any]:
        # Ensure timestamp in UTC
        if "timestamp" not in log_record:
            log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        # Guarantee request_id exists
        log_record.setdefault("request_id", request_id_var.get())
        return log_record


def _ensure_log_dir() -> Path:
    p = Path("data/logs")
    p.mkdir(parents=True, exist_ok=True)
    return p


def _build_handlers() -> List[logging.Handler]:
    log_dir = _ensure_log_dir()
    file_path = log_dir / "app.log"

    # Rotating file handler
    file_handler = RotatingFileHandler(
        filename=str(file_path),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding="utf-8",
    )

    # Stream handler for stdout (Cloud Run / dev)
    stream_handler = logging.StreamHandler()

    # JSON formatter (consistent across handlers)
    fmt_keys = [
        "timestamp",
        "levelname",
        "name",
        "message",
        "record_type",  # "access" for uvicorn access lines
        "request_id",
        "client_addr",
        "method",
        "path",
        "http_version",
        "status_code",
        "pathname",
        "lineno",
        "funcName",
    ]
    formatter = UtcJsonFormatter(json.dumps({k: f"%({k})s" for k in fmt_keys}))

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # Inject request_id on all records
    rid_filter = RequestIdFilter()
    file_handler.addFilter(rid_filter)
    stream_handler.addFilter(rid_filter)

    # Normalize uvicorn access logs
    access_filter = UvicornAccessFilter()
    file_handler.addFilter(access_filter)
    stream_handler.addFilter(access_filter)

    return [file_handler, stream_handler]


def _attach_handlers(logger: logging.Logger, handlers: List[logging.Handler], level: int) -> None:
    logger.setLevel(level)
    if not getattr(logger, "_monkeypaw_handlers", False):
        logger.handlers.clear()
        for h in handlers:
            logger.addHandler(h)
        setattr(logger, "_monkeypaw_handlers", True)


def _configure_root_logger(level: int = logging.INFO) -> None:
    handlers = _build_handlers()

    _attach_handlers(logging.getLogger(), handlers, level)
    # Align uvicorn/starlette loggers with the same handlers/level
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "starlette"):
        _attach_handlers(logging.getLogger(name), handlers, level)


def _set_request_id_from_request(request: Request, response: Response) -> str:
    """
    Determine request_id precedence and persist to response + contextvar.

    Priority:
    1) Incoming 'X-Request-ID' header
    2) request.state.request_id (maybe set by other middleware/routes)
    3) generate a UUID4
    """
    rid = request.headers.get("x-request-id") or getattr(getattr(request, "state", object()), "request_id", "") or ""
    if not rid:
        rid = str(uuid4())
        try:
            request.state.request_id = rid  # type: ignore[attr-defined]
        except AttributeError:
            # If request.state is not settable, just continue; header + contextvar still work.
            pass

    response.headers["X-Request-ID"] = rid
    request_id_var.set(rid)
    return rid


def _install_request_id_middleware(app: FastAPI) -> None:
    # Idempotent guard on the app instance (public name to avoid "protected" lint).
    if getattr(app.state, "monkeypaw_rid_mw", False):
        return

    @app.middleware("http")
    async def _rid_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = Response("Internal server error", status_code=500)
        _set_request_id_from_request(request, response)
        try:
            response = await call_next(request)
        finally:
            # Ensure the header survived downstream
            rid = request_id_var.get()
            response.headers.setdefault("X-Request-ID", rid)
        return response

    app.state.monkeypaw_rid_mw = True  # type: ignore[attr-defined]


def setup_logging(app: FastAPI) -> None:
    """
    Configure JSON logging + request_id middleware (idempotent).
    Call once right after app = FastAPI(...).
    """
    if getattr(app.state, "monkeypaw_logging", False):
        return

    # Level can be overridden by env (e.g., INFO/DEBUG/WARNING)
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    _configure_root_logger(level)
    _install_request_id_middleware(app)

    app.state.monkeypaw_logging = True  # type: ignore[attr-defined]
