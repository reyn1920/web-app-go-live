"""Health and status endpoints."""

import platform
import shutil
import time
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/system/status")
def status() -> Dict[str, Any]:
    """
    Get comprehensive system status information.

    Returns:
        Dict containing system status, platform info, tools, and disk usage
    """
    tools = {"ffmpeg": bool(shutil.which("ffmpeg")), "python": True}
    mem = shutil.disk_usage(".")
    return {
        "ok": True,
        "time": time.time(),
        "platform": platform.platform(),
        "tools": tools,
        "disk": {"free": mem.free, "total": mem.total},
    }


@router.get("/system/pauses")
def pauses() -> Dict[str, Any]:
    """
    Get current system pause status.

    Returns:
        Dict containing pause status information
    """
    return {"ok": True, "pauses": {}}
