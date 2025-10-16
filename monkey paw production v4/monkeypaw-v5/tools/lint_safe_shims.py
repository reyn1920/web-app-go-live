"""
Add-only lint helpers:
- no_op(): assign to unused vars to silence F841 without altering logic
- use(): reference names to silence F401 in rare dynamic-import cases
"""

from __future__ import annotations

from typing import Any


def no_op(*args: Any, **kwargs: Any) -> None:
    """Utility to mark variables as intentionally unused."""
    return None


def use(*names: Any) -> None:
    """Mark imported symbols as 'used' for dynamic imports."""
    return None
