from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
def health():
    return {"status": "ok"}


@health_router.get("/api/health")
def api_health():
    return {"status": "ok"}


@health_router.get("/status")
def status():
    return {"status": "ok"}


@health_router.get("/api/status")
def api_status():
    return {"status": "ok"}


@health_router.get("/")
def root():
    return {"status": "ok"}
