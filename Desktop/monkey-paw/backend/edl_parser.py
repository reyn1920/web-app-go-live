"""
Professional EDL (Edit Decision List) parser for video editing workflows.

This module provides functionality to parse standard EDL files and extract
timeline information including clips, timecodes, and metadata.
"""

import re
from typing import Any, Dict, List, Optional

# Timecode pattern: HH:MM:SS:FF (hours:minutes:seconds:frames)
TIMECODE_PATTERN = re.compile(r"(\d{2}):(\d{2}):(\d{2}):(\d{2})")


def timecode_to_frames(timecode: str, fps: int = 30) -> int:
    """
    Convert timecode string to frame count.

    Args:
        timecode: Timecode string in HH:MM:SS:FF format
        fps: Frames per second for conversion

    Returns:
        Total frame count as integer
    """
    match = TIMECODE_PATTERN.match(timecode.strip())
    if not match:
        return 0

    hours, minutes, seconds, frames = map(int, match.groups())
    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    return (total_seconds * fps) + frames


def frames_to_seconds(frame_count: int, fps: int = 30) -> float:
    """
    Convert frame count to duration in seconds.

    Args:
        frame_count: Number of frames
        fps: Frames per second for conversion

    Returns:
        Duration in seconds as float
    """
    return frame_count / float(fps)


def _parse_edl_event_line(line: str, fps: int) -> Optional[Dict[str, Any]]:
    """
    Parse a single EDL event line.

    Args:
        line: EDL line containing event data
        fps: Frames per second for timecode conversion

    Returns:
        Event dictionary if line is valid EDL event, None otherwise
    """
    # EDL event pattern: EVENT# REEL TRACK TRANS SRC_IN SRC_OUT REC_IN REC_OUT
    pattern = (
        r"^(\d{3})\s+\S+\s+(V|A|VA)\s+\S+\s+"
        r"(\d{2}:\d{2}:\d{2}:\d{2})\s+"
        r"(\d{2}:\d{2}:\d{2}:\d{2})\s+"
        r"(\d{2}:\d{2}:\d{2}:\d{2})\s+"
        r"(\d{2}:\d{2}:\d{2}:\d{2})"
    )

    match = re.match(pattern, line)
    if not match:
        return None

    # Extract matched groups
    event_num = int(match.group(1))
    track_type = match.group(2)
    src_in = match.group(3)
    src_out = match.group(4)
    rec_in = match.group(5)
    rec_out = match.group(6)

    # Calculate duration
    rec_in_frames = timecode_to_frames(rec_in, fps)
    rec_out_frames = timecode_to_frames(rec_out, fps)
    duration_frames = rec_out_frames - rec_in_frames
    duration_seconds = frames_to_seconds(duration_frames, fps)

    return {
        "event": event_num,
        "track": track_type,
        "src_in": src_in,
        "src_out": src_out,
        "rec_in": rec_in,
        "rec_out": rec_out,
        "duration_secs": duration_seconds,
        "clip_name": None,
        "file": None,
    }


def _parse_edl_metadata_line(line: str, current_event: Dict[str, Any]) -> None:
    """
    Parse EDL metadata lines and update current event.

    Args:
        line: EDL line containing metadata
        current_event: Current event dictionary to update
    """
    # Parse clip name
    clip_name_match = re.match(r"^\* FROM CLIP NAME:\s*(.+)", line)
    if clip_name_match:
        current_event["clip_name"] = clip_name_match.group(1).strip()
        return

    # Parse source file
    source_file_match = re.match(r"^\* SOURCE FILE:\s*(.+)", line)
    if source_file_match:
        current_event["file"] = source_file_match.group(1).strip()


def parse_edl(edl_path: str, fps: int = 30) -> List[Dict[str, Any]]:
    """
    Parse EDL file and extract timeline events.

    Args:
        edl_path: Path to EDL file
        fps: Frames per second for timecode conversion (default: 30)

    Returns:
        List of event dictionaries with timing and metadata

    Raises:
        FileNotFoundError: If EDL file doesn't exist
        IOError: If file cannot be read
    """
    events: List[dict[str, Any]] = []
    current_event: Optional[dict[str, Any]] = None

    try:
        with open(edl_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.read().splitlines()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"EDL file not found: {edl_path}") from exc
    except IOError as exc:
        raise IOError(f"Cannot read EDL file: {edl_path}") from exc

    for line in lines:
        # Try to parse as event line
        event = _parse_edl_event_line(line, fps)
        if event:
            events.append(event)
            current_event = event
            continue

        # Try to parse as metadata line
        if current_event:
            _parse_edl_metadata_line(line, current_event)

    return events
