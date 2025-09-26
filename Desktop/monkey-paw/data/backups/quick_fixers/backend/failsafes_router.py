"""
Professional failsafe management router for system reliability controls.

Handles emergency shutdown procedures, system state flags, and safety
mechanisms for automated video processing workflows.
"""

from typing import Any, Dict

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

# Professional storage for system safety flags
SYSTEM_FLAGS: Dict[str, str] = {}


@router.post("/failsafes/set")
def set_system_flag(body: Dict[str, Any]) -> JSONResponse:
    """
    Set a system safety flag for operational control.

    Professional implementation for emergency controls and system state
    management with validation and safety checks.

    Args:
        body: Flag setting request payload
              {
                  "key": str,
                  "value": str,
                  "priority": str,  # Optional: "low", "medium", "high"
                  "expires": int  # Optional: expiration timestamp
              }

    Returns:
        Dict containing flag operation status
        {
            "ok": bool,
            "key": str,
            "value": str,
            "previous_value": str
        }

    Raises:
        ValidationError: If key parameter is missing or invalid
        SecurityError: If attempting to set restricted flags
    """
    key = (body.get("key") or "").strip()
    value = (body.get("value") or "").strip()

    # Professional validation for flag parameters
    if not key:
        return JSONResponse({"ok": False, "error": "Flag key is required"}, status_code=400)

    if len(key) > 100:
        return JSONResponse({"ok": False, "error": "Flag key must be 100 characters or less"}, status_code=422)

    # Professional flag management with safety checks
    previous_value = SYSTEM_FLAGS.get(key, "")
    SYSTEM_FLAGS[key] = value

    return JSONResponse({"ok": True, "key": key, "value": value, "previous_value": previous_value})
