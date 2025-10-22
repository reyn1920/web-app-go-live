"""
Google Drive Desktop Integration
Ensures all app I/O goes through the real mount with no stray writes
"""

import os
import pathlib
from subprocess import check_output, STDOUT


def desktop_root():
    """
    Get the Google Drive desktop mount root path.
    
    Uses intelligent detection to find the active mount and ensures
    all app I/O goes through the correct mount to prevent stray writes.
    
    Returns:
        pathlib.Path: Path to the Google Drive desktop mount
        
    Raises:
        RuntimeError: If no Google Drive mount is found
    """
    root = os.getenv("DRIVE_DESKTOP_ROOT", "").strip()
    if not root and os.getenv("DRIVE_DESKTOP_ROOT_AUTO", "1") == "1":
        try:
            out = check_output(
                ["/opt/homebrew/bin/python3.11", "tools/drive_desktop_detect.py"],
                stderr=STDOUT, text=True
            ).strip()
            if out and out != "NO_MOUNT":
                root = out
        except Exception:
            pass
    if not root:
        raise RuntimeError("Google Drive desktop mount not found. Open Google Drive and sign in.")
    return pathlib.Path(root)


def get_drive_path(relative_path=""):
    """
    Get a full path within the Google Drive mount.
    
    Args:
        relative_path (str): Relative path within the drive mount
        
    Returns:
        pathlib.Path: Full path within the drive mount
    """
    drive_root = desktop_root()
    if relative_path:
        return drive_root / relative_path
    return drive_root


def ensure_drive_access():
    """
    Ensure Google Drive mount is accessible.
    
    Raises:
        RuntimeError: If drive mount is not accessible
    """
    drive_root = desktop_root()
    if not drive_root.exists():
        raise RuntimeError(f"Google Drive mount not accessible: {drive_root}")
    if not drive_root.is_dir():
        raise RuntimeError(f"Google Drive mount is not a directory: {drive_root}")
    return drive_root
