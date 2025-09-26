import io
import json
import logging

from fastapi.testclient import TestClient

try:
    from backend.main import app
except ModuleNotFoundError:
    from app.main import app


def test_json_logging_emits_request_id_and_path(monkeypatch) -> None:
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
    try:
        client = TestClient(app)
        r = client.get("/api/health")
        assert r.status_code == 200
    finally:
        root.removeHandler(handler)
    lines = [ln for ln in log_stream.getvalue().splitlines() if ln.strip()]
    assert lines, "Expected at least one log line from middleware"
    parsed = None
    for ln in reversed(lines):
        try:
            parsed = json.loads(ln)
            break
        except Exception:
            continue
    assert isinstance(parsed, dict)
    assert "request_id" in parsed and isinstance(parsed["request_id"], str)
    assert parsed.get("path") == "/api/health"
