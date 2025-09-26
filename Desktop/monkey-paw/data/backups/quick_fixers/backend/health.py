"""
Professional health check router for service monitoring.

This module provides comprehensive health check endpoints for monitoring
the availability and status of the video automation API service.
"""

import datetime
from typing import Any, Dict

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
def get_health_status(request: Request) -> Dict[str, Any]:
    """
    Return comprehensive health status of the API service.

    Returns:
        Dictionary with detailed service status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "service": "monkey-paw-backend",
        "port": 8010,
        "version": "1.0.0",
        "request_id": getattr(request.state, "request_id", request.headers.get("x-request-id", "")),
    }
