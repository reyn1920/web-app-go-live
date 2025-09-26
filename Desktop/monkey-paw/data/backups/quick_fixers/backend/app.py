from abtest_router import router as abtest_router
from captions_router import router as captions_router
from channel_presets_router import router as channel_presets_router
from compliance_router import router as compliance_router
from dupe_router import router as dupe_router
from failsafes_router import router as failsafes_router
from fastapi import FastAPI
from .app_health_router import health_router
from health import router as health_router
from integrations_router import router as integrations_router
from link_rotator_router import router as link_rotator_router
from manifest_ingest_router import router as manifest_ingest_router
from outro_router import router as outro_router
from scheduler_router import router as scheduler_router
from seo_router import router as seo_router
from status_router import router as status_router

app = FastAPI()

app.include_router(channel_presets_router, prefix="/api")
app.include_router(scheduler_router, prefix="/api")
app.include_router(compliance_router, prefix="/api")
app.include_router(manifest_ingest_router, prefix="/api")
app.include_router(outro_router, prefix="/api")
app.include_router(status_router, prefix="/api")
app.include_router(failsafes_router, prefix="/api")
app.include_router(abtest_router, prefix="/api")
app.include_router(link_rotator_router, prefix="/api")
app.include_router(seo_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(integrations_router, prefix="/api")
app.include_router(dupe_router, prefix="/api")
app.include_router(captions_router, prefix="/api")

app.include_router(health_router)
