from fastapi import FastAPI
from .app_health_router import health_router
from .rate_limit_guard import RateLimitMiddleware

# Create FastAPI app
app = FastAPI()

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include health router
app.include_router(health_router)

# Optional routers (import if present)
import logging

logger = logging.getLogger(__name__)

def _include_optional_router(module_name: str, attr_name: str = "router") -> None:
    """Include a router if the module exists and has the specified attribute."""
    try:
        mod = __import__(f"{__package__}.{module_name}", fromlist=[attr_name])
        router = getattr(mod, attr_name)
        app.include_router(router, prefix="/api")
        logger.info("Included router: %s.%s", module_name, attr_name)
    except (ImportError, AttributeError) as exc:
        logger.warning("Skipping optional router %s: %s", module_name, exc)

# Try to include these routers only if present
_include_optional_router("abtest_router", "router")
_include_optional_router("captions_router", "router")
_include_optional_router("channel_presets_router", "router")
_include_optional_router("compliance_router", "router")
_include_optional_router("dupe_router", "router")
_include_optional_router("failsafes_router", "router")
_include_optional_router("integrations_router", "router")
_include_optional_router("link_rotator_router", "router")
_include_optional_router("manifest_ingest_router", "router")
_include_optional_router("outro_router", "router")
_include_optional_router("scheduler_router", "router")
_include_optional_router("seo_router", "router")
_include_optional_router("status_router", "router")