"""
Professional FCPXML parser for Final Cut Pro timeline processing.

This module provides functionality to parse Final Cut Pro XML files and
extract timeline events, assets, titles, and voiceover regions.
"""

from typing import Any, Dict, List

import defusedxml.ElementTree as ET


def parse_rational_seconds(time_string: str) -> float:
    """
    Parse Final Cut Pro rational time format to seconds.

    Args:
        time_string: Time string in format like '60/1s' or '1.5s'

    Returns:
        Time value in seconds as float
    """
    normalized_time = (time_string or "").strip()

    if not normalized_time:
        return 0.0

    # Remove 's' suffix if present
    if normalized_time.endswith("s"):
        normalized_time = normalized_time[:-1]

    # Handle fractional format (e.g., '60/1')
    if "/" in normalized_time:
        try:
            numerator, denominator = normalized_time.split("/", 1)
            return float(numerator) / float(denominator)
        except (ValueError, ZeroDivisionError):
            return 0.0

    # Handle decimal format
    try:
        return float(normalized_time)
    except ValueError:
        return 0.0


def _extract_namespace(root_element: Any) -> Dict[str, str]:
    """
    Extract XML namespace from root element.

    Args:
        root_element: XML root element

    Returns:
        Namespace dictionary for XPath queries
    """
    if "}" in root_element.tag:
        namespace_uri = root_element.tag.split("}")[0].strip("{")
        return {"fcpx": namespace_uri}
    return {}


def _parse_assets(root_element: Any, namespace: Dict[str, str]) -> Dict[str, Dict]:
    """
    Parse asset definitions from FCPXML.

    Args:
        root_element: XML root element
        namespace: XML namespace dictionary

    Returns:
        Dictionary mapping asset IDs to asset data
    """
    assets = {}

    # Build XPath expression
    asset_xpath = ".//fcpx:asset" if namespace else ".//asset"

    for asset_element in root_element.findall(asset_xpath, namespace):
        asset_id = asset_element.get("id")
        if asset_id:
            assets[asset_id] = {
                "name": asset_element.get("name", ""),
                "src": asset_element.get("src", ""),
            }

    return assets


def _parse_timeline_events(
    root_element: Any, namespace: Dict[str, str], assets: Dict[str, Dict]
) -> List[Dict[str, Any]]:
    """
    Parse timeline events from asset clips.

    Args:
        root_element: XML root element
        namespace: XML namespace dictionary
        assets: Asset mapping dictionary

    Returns:
        List of timeline event dictionaries
    """
    events = []

    # Build XPath expression
    clip_xpath = ".//fcpx:asset-clip" if namespace else ".//asset-clip"

    for clip_element in root_element.findall(clip_xpath, namespace):
        asset_ref = clip_element.get("ref", "")
        clip_name = clip_element.get("name", "")

        # Get asset info
        asset_info = assets.get(asset_ref, {})
        final_name = clip_name or asset_info.get("name", "")

        # Parse timing
        duration = parse_rational_seconds(clip_element.get("duration", "0s"))
        start_time = parse_rational_seconds(clip_element.get("offset") or clip_element.get("start", "0s"))
        end_time = start_time + duration

        events.append(
            {
                "name": final_name,
                "ref": asset_ref,
                "src": asset_info.get("src", ""),
                "duration_secs": duration,
                "start_secs": start_time,
                "end_secs": end_time,
            }
        )

    return events


def _parse_title_regions(root_element: Any, namespace: Dict[str, str]) -> List[Dict[str, float]]:
    """
    Parse title overlay regions from FCPXML.

    Args:
        root_element: XML root element
        namespace: XML namespace dictionary

    Returns:
        List of title region dictionaries with timing
    """
    title_regions = []

    # Build XPath expression
    title_xpath = ".//fcpx:title" if namespace else ".//title"

    for title_element in root_element.findall(title_xpath, namespace):
        duration = parse_rational_seconds(title_element.get("duration", "0s"))
        start_time = parse_rational_seconds(title_element.get("offset") or title_element.get("start", "0s"))
        end_time = start_time + duration

        title_regions.append({"start_secs": start_time, "end_secs": end_time})

    return title_regions


def _detect_voiceover_regions(root_element: Any, namespace: Dict[str, str]) -> List[Dict[str, float]]:
    """
    Detect voiceover regions based on audio role or naming patterns.

    Args:
        root_element: XML root element
        namespace: XML namespace dictionary

    Returns:
        List of voiceover region dictionaries
    """
    vo_regions = []
    voiceover_keywords = ["vo", "narration", "dialogue", "voiceover"]

    # Build XPath expression
    clip_xpath = ".//fcpx:asset-clip" if namespace else ".//asset-clip"

    for clip_element in root_element.findall(clip_xpath, namespace):
        # Check audio role and name for voiceover indicators
        audio_role = (clip_element.get("audioRole", "") or clip_element.get("role", "")).lower()
        clip_name = (clip_element.get("name", "")).lower()

        # Check if this clip contains voiceover content
        is_voiceover = any(keyword in audio_role or keyword in clip_name for keyword in voiceover_keywords)

        if is_voiceover:
            duration = parse_rational_seconds(clip_element.get("duration", "0s"))
            start_time = parse_rational_seconds(clip_element.get("offset") or clip_element.get("start", "0s"))
            end_time = start_time + duration

            vo_regions.append({"start_secs": start_time, "end_secs": end_time})

    return vo_regions


def parse_fcpxml(xml_path: str) -> Dict[str, Any]:
    """
    Parse Final Cut Pro XML file and extract timeline data.

    Args:
        xml_path: Path to FCPXML file

    Returns:
        Dictionary containing parsed timeline data with keys:
        - assets: Asset mapping dictionary
        - events: Timeline events list
        - titles: Title regions list
        - vo_regions: Voiceover regions list

    Raises:
        ET.ParseError: If XML file is malformed
        FileNotFoundError: If XML file doesn't exist
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract namespace information
    namespace = _extract_namespace(root)

    # Parse all components
    assets = _parse_assets(root, namespace)
    events = _parse_timeline_events(root, namespace, assets)
    titles = _parse_title_regions(root, namespace)
    vo_regions = _detect_voiceover_regions(root, namespace)

    return {
        "assets": assets,
        "events": events,
        "titles": titles,
        "vo_regions": vo_regions,
    }
