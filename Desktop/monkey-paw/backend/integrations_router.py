"""
Professional integrations router for external tool availability checking.

This module provides REST API endpoint to check availability of required
external tools and environment variables for the video automation system.
"""

import os
import shutil
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter()

# Required external tools for video processing
REQUIRED_TOOLS: List[str] = ["ffmpeg", "git", "node", "rclone", "whisper"]

# Required environment variables for API integrations
REQUIRED_ENV_KEYS: List[str] = [
    "BLENDER_BIN",
    "GOOGLE_DRIVE_MOUNT",
    "ELEVENLABS_API_KEY",
    "SPEECHELO_KEY",
    "OPENAI_API_KEY",
    "YOUTUBE_API_KEY",
]


@router.get("/integrations")
def check_integrations() -> Dict[str, Any]:
    """
    Check availability of external tools and environment variables.

    Returns:
        Dictionary containing integration status for tools and environment
    """
    # Check tool availability in system PATH
    tool_status = {}
    for tool in REQUIRED_TOOLS:
        tool_status[tool] = bool(shutil.which(tool))

    # Special handling for Blender (custom installation path)
    blender_path = os.environ.get("BLENDER_BIN", "/Applications/Blender.app/Contents/MacOS/Blender")
    tool_status["blender"] = os.path.exists(blender_path)

    # Check environment variable configuration
    env_status = {}
    for env_key in REQUIRED_ENV_KEYS:
        env_status[env_key] = "set" if os.environ.get(env_key) else "missing"

    return {"ok": True, "tools": tool_status, "env": env_status}
