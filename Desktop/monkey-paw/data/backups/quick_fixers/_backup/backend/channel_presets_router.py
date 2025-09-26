"""
Channel presets router for managing channel-specific configuration presets.

This module handles CRUD operations for channel presets including loading,
saving, updating, and retrieving channel configurations.
"""

import json
import os
from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter()

# Store channel configuration in memory (in runtime, use a database)
_channel_config: Dict[str, Any] = {}


@router.post("/channel_presets/set")
def set_presets(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set and persist channel presets configuration.

    Args:
        body: Dictionary containing channel configuration data

    Returns:
        Dict containing operation status and applied channel information
    """

    channels: Dict[str, Any] = body.get("channels", {})
    _channel_config.clear()
    _channel_config.update(channels)

    # Also save to file for persistence
    base_dir = os.path.dirname(os.path.dirname(__file__))
    config_path = os.path.join(base_dir, "config", "channels_active.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump({"channels": _channel_config}, f, indent=2)

    return {
        "ok": True,
        "applied": list(channels.keys()),
        "total_channels": len(_channel_config),
    }


@router.get("/channel_presets/get")
def get_presets() -> Dict[str, Any]:
    """
    Retrieve current channel presets configuration.

    Returns:
        Dict containing channel configuration and count information
    """

    return {"ok": True, "channels": _channel_config, "count": len(_channel_config)}


# Accessor for _channel_config (for linter and future-proofing)
def get_channel_config() -> Dict[str, Any]:
    """
    Accessor for the in-memory channel configuration.
    Returns:
        The current channel configuration dictionary.
    """
    return _channel_config
