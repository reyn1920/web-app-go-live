"""Site customization for Monkey Paw production environment.

Loads environment variables and provides stubs for optional dependencies.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Environment file search paths
_ENV_CANDIDATES = [
    Path.home() / ".env",
    Path.home() / "monkeypaw-v5" / ".env",
    Path("/Users/thomasbrianreynolds/Google Drive/My Drive/monkey paw production v4/.env"),
    Path("/Users/thomasbrianreynolds/Google Drive/My Drive/monkey paw production v4/secrets.env"),
    Path.cwd() / ".env",
]


def _load_dotenv() -> None:
    """Load environment variables from .env files in priority order."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    for env_path in _ENV_CANDIDATES:
        try:
            if env_path.exists():
                load_dotenv(env_path)
        except (OSError, RuntimeError):
            # Skip files that exist but can't be read
            pass


_load_dotenv()
os.environ.setdefault("SELENIUM_REMOTE_DEBUG_ADDR", "127.0.0.1:9222")


def _stub_redis() -> None:
    """Install a no-op redis stub if redis package is not available."""
    try:
        import redis  # noqa: F401
        return
    except ImportError:
        import types

        stub = types.ModuleType("redis")

        class _DummyRedis:
            """Dummy Redis client that accepts all calls but does nothing."""

            def __init__(self, *_args, **_kwargs) -> None:
                # No-op stub
                pass

            def set(self, *_args, **_kwargs) -> None:
                # No-op stub
                return None

            def get(self, *_args, **_kwargs) -> None:
                # No-op stub
                return None

            def publish(self, *_args, **_kwargs) -> None:
                # No-op stub
                return None

            def close(self) -> None:
                # No-op stub
                pass

        def redis_factory(*_args, **_kwargs) -> _DummyRedis:
            return _DummyRedis(*_args, **_kwargs)

        stub.Redis = redis_factory  # type: ignore[attr-defined]
        sys.modules["redis"] = stub


def _stub_psycopg2() -> None:
    """Install a minimal psycopg2 stub if psycopg2 package is not available."""
    try:
        import psycopg2  # noqa: F401
        return
    except ImportError:
        import types

        stub = types.ModuleType("psycopg2")

        class _DummyConn:
            """Dummy PostgreSQL connection that raises on actual use."""

            def cursor(self):
                raise RuntimeError("psycopg2 not installed (stub in use)")

            def commit(self) -> None:
                # No-op stub
                pass

            def close(self) -> None:
                # No-op stub
                pass

        def connect(*_args, **_kwargs) -> _DummyConn:
            return _DummyConn()

        stub.connect = connect  # type: ignore[attr-defined]
        sys.modules["psycopg2"] = stub


_stub_redis()
_stub_psycopg2()
os.environ.setdefault("FEATURE_REDIS", "0")
os.environ.setdefault("FEATURE_PG", "0")
