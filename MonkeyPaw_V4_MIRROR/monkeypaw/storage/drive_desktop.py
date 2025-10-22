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


def safe_join(relative_path):
    """
    Safely join a relative path to the Google Drive mount.
    
    This is the primary function for all app I/O operations. It ensures:
    - All writes go to the correct mount (no stray writes)
    - Drive mount is accessible before operations
    - Parent directories are created as needed
    - Fail-fast if mount is unavailable
    
    Args:
        relative_path (str): Relative path within "My Drive"
        
    Returns:
        pathlib.Path: Full path within the Google Drive mount
        
    Raises:
        RuntimeError: If Google Drive mount is not found or not accessible
        
    Example:
        >>> from monkeypaw.storage.drive_desktop import safe_join
        >>> p = safe_join("MonkeyPaw/Videos/output.mp4")
        >>> p.parent.mkdir(parents=True, exist_ok=True)
        >>> p.write_text("content")
    """
    drive_root = ensure_drive_access()
    
    # Build full path: mount_root/My Drive/relative_path
    my_drive = drive_root / "My Drive"
    if not my_drive.exists():
        raise RuntimeError(f"'My Drive' folder not found in mount: {drive_root}")
    
    full_path = my_drive / relative_path
    
    # Create parent directories if needed
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    return full_path
