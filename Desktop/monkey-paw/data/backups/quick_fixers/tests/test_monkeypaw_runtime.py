import requests


def test_runtime_health():
    for url in [
        "http://localhost:8010/api/health",
        "http://localhost:8080/health",
        "http://localhost:8000/health",
        "http://localhost:8000/api/health",
        "http://localhost:8000/status",
        "http://localhost:8000/api/status",
        "http://localhost:8000/",
    ]:
        try:
            resp = requests.get(url, timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") in ["ok", "healthy"]:
                    return
        except Exception:
            pass
    assert False, "No health endpoint returned status ok or healthy"
