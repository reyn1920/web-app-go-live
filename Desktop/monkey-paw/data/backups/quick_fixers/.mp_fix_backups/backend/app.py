from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from .abtest_router import router as abtest_router
from .captions_router import router as captions_router
from .channel_presets_router import router as channel_presets_router
from .compliance_router import router as compliance_router
from .dupe_router import router as dupe_router
from .failsafes_router import router as failsafes_router
from .integrations_router import router as integrations_router
from .link_rotator_router import router as link_rotator_router
from .manifest_ingest_router import router as manifest_ingest_router
from .middleware_logging import setup_logging
from .outro_router import router as outro_router
from .scheduler_router import router as scheduler_router
from .seo_router import router as seo_router
from .status_router import router as status_router

"""
Professional FastAPI application for YouTube automation backend.

Enterprise-grade video processing API with comprehensive routing,
middleware integration, and professional system architecture.
"""


# Professional FastAPI application initialization
app = FastAPI(
    title="YouTube Automation API",
    description="Professional video processing and automation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Register all routers with consistent API prefix
app.include_router(status_router, prefix="/api")
app.include_router(channel_presets_router, prefix="/api")
app.include_router(scheduler_router, prefix="/api")
app.include_router(compliance_router, prefix="/api")
app.include_router(manifest_ingest_router, prefix="/api")
app.include_router(outro_router, prefix="/api")
app.include_router(failsafes_router, prefix="/api")
app.include_router(abtest_router, prefix="/api")
app.include_router(link_rotator_router, prefix="/api")
app.include_router(seo_router, prefix="/api")
app.include_router(integrations_router, prefix="/api")
app.include_router(dupe_router, prefix="/api")
app.include_router(captions_router, prefix="/api")


# Define helper once.
if "_get_or_set_request_id" not in globals():

    def _get_or_set_request_id(request: Request, response: Response) -> str:
        """
        Ensure a request_id exists on the request and response.

        Priority:
        1) Incoming header X-Request-ID
        2) request.state.request_id (if middleware already set it)
        3) Generate a new UUID4

        Always writes X-Request-ID to the response headers.
        """
        rid = (
            request.headers.get("x-request-id") or getattr(getattr(request, "state", object()), "request_id", "") or ""
        )
        if not rid:
            rid = str(uuid4())
            try:
                request.state.request_id = rid
            except AttributeError as exc:
                print(f"Failed to set request_id on request.state: {exc}")
        try:
            response.headers["X-Request-ID"] = rid
        except (TypeError, AttributeError, KeyError) as exc:
            print(f"Failed to set X-Request-ID header: {exc}")
        return rid


# Register /api/health once (don’t duplicate if a router already added it).
def _health_route_already_registered() -> bool:
    try:
        for r in getattr(app.router, "routes", []):
            # Starlette routes have .path or .path_format depending on version
            p = getattr(r, "path", None) or getattr(r, "path_format", None)
            if p == "/api/health":
                return True
    except AttributeError as exc:
        print(f"Failed to check health route: {exc}")
    return False


if not _health_route_already_registered():

    @app.get("/api/health", include_in_schema=False)
    def _api_health(request: Request, response: Response) -> Dict[str, Any]:
        rid = _get_or_set_request_id(request, response)
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "monkey-paw-backend",
            "port": 8010,
            "version": "1.0.0",
            "request_id": rid,
        }
# --- end monkey-paw block ---


# runtime application configuration
# Ensure backend modules can be imported when run as a package
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010)

setup_logging(app)
