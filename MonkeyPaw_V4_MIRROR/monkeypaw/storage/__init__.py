"""
Storage package for MonkeyPaw
Handles Google Drive desktop integration and file storage
"""

from .drive_desktop import desktop_root, get_drive_path, ensure_drive_access, safe_join

__all__ = ["desktop_root", "get_drive_path", "ensure_drive_access", "safe_join"]
