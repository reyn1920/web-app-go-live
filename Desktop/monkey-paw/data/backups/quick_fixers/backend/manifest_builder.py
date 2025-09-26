"""
Professional manifest builder for video timeline processing.

This module provides functionality to convert video events into structured
manifest format for compliance analysis and processing.
"""

import csv
import os
from typing import Any, Dict, List, Optional, Tuple

# Source classification keywords for automated content detection
SOURCE_KEYWORDS = {
    "tv_news": ["cnn", "fox", "msnbc", "nbc", "abcnews", "cbsnews", "news"],
    "social_clip": ["tiktok", "instagram", "reels", "shorts", "twitter", "x.com"],
    "movie": ["trailer", "movie", "filmclip"],
    "music_video": ["vevo", "musicvideo", "mv_"],
}


def load_mapping(csv_path: str) -> List[Dict[str, str]]:
    """
    Load source mapping data from CSV file.

    Args:
        csv_path: Path to CSV mapping file

    Returns:
        List of mapping dictionaries
    """
    mappings: List[Dict[str, Any]] = []

    if not csv_path or not os.path.exists(csv_path):
        return mappings

    try:
        with open(csv_path, "r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                mappings.append(row)
    except (OSError, csv.Error):
        # Return empty list if file cannot be read
        pass

    return mappings


def classify_source(name: str, path: str, mapping: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Classify video source based on name, path and mapping data.

    Args:
        name: Video clip name
        path: File path or URL
        mapping: Source mapping data

    Returns:
        Dictionary with source classification data
    """
    normalized_name = (name or "").lower()
    normalized_path = (path or "").lower()

    # Check explicit mapping first
    for row in mapping:
        key = (row.get("name_or_path") or "").lower()
        if key and (key in normalized_name or key in normalized_path):
            return {
                "source": (row.get("source") or "original").lower(),
                "src_url": row.get("src_url") or "",
                "attrib_text": row.get("attribution_text") or "",
            }

    # Check keyword patterns
    for source_type, keywords in SOURCE_KEYWORDS.items():
        name_match = any(keyword in normalized_name for keyword in keywords)
        path_match = any(keyword in normalized_path for keyword in keywords)

        if name_match or path_match:
            return {"source": source_type, "src_url": "", "attrib_text": ""}

    # Default to original content
    return {"source": "original", "src_url": "", "attrib_text": ""}


def calculate_overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    """
    Calculate temporal overlap between two time ranges.

    Args:
        start_a: Start time of range A
        end_a: End time of range A
        start_b: Start time of range B
        end_b: End time of range B

    Returns:
        Overlap duration in seconds
    """
    overlap_start = max(start_a, start_b)
    overlap_end = min(end_a, end_b)
    return max(0.0, overlap_end - overlap_start)


def _process_original_segment(
    name: str, duration: float, start_time: float, end_time: float, has_overlay: bool
) -> Dict[str, Any]:
    """
    Create manifest entry for original content segment.

    Args:
        name: Segment label/name
        duration: Duration in seconds
        start_time: Start timestamp
        end_time: End timestamp
        has_overlay: Whether segment has text overlay

    Returns:
        Original segment dictionary
    """
    return {
        "type": "original",
        "label": name,
        "duration": duration,
        "start": start_time,
        "end": end_time,
        "transformations": {
            "overlay_text": has_overlay,
            "voiceover": False,
            "pip_or_crop": False,
        },
    }


def _process_third_party_segment(
    classification: Dict[str, str],
    duration: float,
    start_time: float,
    end_time: float,
    has_voiceover: bool,
    has_overlay: bool,
    vo_overlap_secs: float,
    overlay_overlap_secs: float,
) -> Dict[str, Any]:
    """
    Create manifest entry for third-party content segment.

    Args:
        classification: Source classification data
        duration: Duration in seconds
        start_time: Start timestamp
        end_time: End timestamp
        has_voiceover: Whether segment has voiceover
        has_overlay: Whether segment has text overlay
        vo_overlap_secs: Voiceover overlap duration
        overlay_overlap_secs: Overlay overlap duration

    Returns:
        Third-party segment dictionary
    """
    return {
        "type": "third_party",
        "source": classification["source"],
        "src_url": classification["src_url"],
        "duration": duration,
        "start": start_time,
        "end": end_time,
        "transformations": {
            "voiceover": has_voiceover,
            "overlay_text": has_overlay,
            "pip_or_crop": True,
            "vo_overlap_secs": vo_overlap_secs,
            "overlay_overlap_secs": overlay_overlap_secs,
        },
        "attribution": {
            "onscreen": bool(classification["attrib_text"]),
            "text": classification["attrib_text"],
        },
    }


def _calculate_region_overlaps(
    start_time: float,
    end_time: float,
    title_regions: List[Dict[str, float]],
    vo_regions: List[Dict[str, float]],
) -> Tuple[float, float]:
    """
    Calculate overlay and voiceover coverage for a time segment.

    Args:
        start_time: Segment start time
        end_time: Segment end time
        title_regions: List of title overlay regions
        vo_regions: List of voiceover regions

    Returns:
        Tuple of (title_overlap_total, vo_overlap_total)
    """
    title_overlap_total = sum(
        calculate_overlap(
            start_time,
            end_time,
            region.get("start_secs", 0.0),
            region.get("end_secs", 0.0),
        )
        for region in title_regions
    )

    vo_overlap_total = sum(
        calculate_overlap(
            start_time,
            end_time,
            region.get("start_secs", 0.0),
            region.get("end_secs", 0.0),
        )
        for region in vo_regions
    )

    return title_overlap_total, vo_overlap_total


def events_to_manifest(
    events: List[Dict[str, Any]],
    mapping: List[Dict[str, str]],
    slug: str,
    title_regions: Optional[List[Dict[str, float]]] = None,
    vo_regions: Optional[List[Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """
    Convert timeline events to structured manifest format.

    Args:
        events: List of timeline event dictionaries
        mapping: Source classification mapping
        slug: Content identifier slug
        title_regions: Optional list of title overlay regions
        vo_regions: Optional list of voiceover regions

    Returns:
        Structured manifest dictionary
    """
    title_regions = title_regions or []
    vo_regions = vo_regions or []
    segments: List[Dict[str, Any]] = []

    for event in events:
        # Extract event data
        name = event.get("name", "")
        source_path = event.get("src", "")
        duration = float(event.get("duration_secs", 0.0))
        start_time = float(event.get("start_secs", 0.0))
        end_time = float(event.get("end_secs", start_time + duration))

        # Classify source
        classification = classify_source(name, source_path, mapping)

        # Calculate region overlaps
        title_overlap: float
        vo_overlap: float
        title_overlap, vo_overlap = _calculate_region_overlaps(start_time, end_time, title_regions, vo_regions)

        # Determine transformation flags
        has_overlay: bool = title_overlap >= 0.2 * duration if duration > 0 else False
        has_voiceover: bool = vo_overlap >= 0.5 * duration if duration > 0 else False

        # Create appropriate segment type
        if classification["source"] == "original":
            segment = _process_original_segment(name, duration, start_time, end_time, has_overlay)
        else:
            segment = _process_third_party_segment(
                classification,
                duration,
                start_time,
                end_time,
                has_voiceover,
                has_overlay,
                vo_overlap,
                title_overlap,
            )

        segments.append(segment)

    # Build final manifest
    has_third_party = any(segment.get("type") == "third_party" for segment in segments)

    return {"slug": slug, "uses_third_party": has_third_party, "segments": segments}
