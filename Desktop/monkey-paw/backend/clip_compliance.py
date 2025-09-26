"""Compliance checks for generated clips."""

import json
from typing import Any, Dict, List, Optional

DEFAULT_RULES: Dict[str, Any] = {
    "max_continuous_by_source": {
        "tv_news": 8.0,
        "talk_show": 6.0,
        "movie": 5.0,
        "music_video": 5.0,
        "social_clip": 12.0,
        "unknown": 6.0,
    },
    "max_total_third_party_secs": 90.0,
    "min_transform_ratio": 0.6,
    "require_attribution": True,
    "require_overlay_pct": 0.5,
}


def _load_manifest_data(manifest_path: str) -> Dict[str, Any]:
    """
    Load manifest data from JSON file.

    Args:
        manifest_path: Path to timeline manifest JSON file

    Returns:
        Parsed manifest data dictionary
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data: Dict[str, Any] = json.load(f)
        return manifest_data


def _process_segment_compliance(segment_idx: int, segment: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process individual segment for compliance violations.

    Args:
        segment_idx: Index of segment in timeline
        segment: Segment data dictionary
        rules: Compliance rules dictionary

    Returns:
        Dictionary with segment metrics and violations
    """
    duration = float(segment.get("duration", 0.0) or 0.0)
    source = (segment.get("source") or "unknown").lower()
    violations: List[str] = []

    # Check per-clip duration limits
    limit = rules["max_continuous_by_source"].get(source, rules["max_continuous_by_source"]["unknown"])

    if duration > limit + 1e-3:
        violations.append(f"Clip {segment_idx} from {source} exceeds per-clip limit: {duration:.1f}s > {limit:.1f}s")

    # Check transformations
    transformations = segment.get("transformations", {})
    has_overlay = transformations.get("overlay_text") or transformations.get("pip_or_crop")

    vo_overlap = transformations.get("vo_overlap_secs", 0.0)
    if transformations.get("voiceover") and not vo_overlap:
        vo_overlap = duration

    commentary_secs = float(vo_overlap or 0.0)

    return {
        "duration": duration,
        "has_overlay": has_overlay,
        "commentary_secs": commentary_secs,
        "violations": violations,
    }


def _validate_aggregate_compliance(
    total_duration: float,
    overlay_count: int,
    total_clips: int,
    commentary_secs: float,
    rules: Dict[str, Any],
) -> List[str]:
    """
    Validate aggregate compliance metrics.

    Args:
        total_duration: Total third-party content duration
        overlay_count: Number of clips with overlays
        total_clips: Total number of third-party clips
        commentary_secs: Total commentary seconds
        rules: Compliance rules dictionary

    Returns:
        List of violation messages
    """
    violations: List[str] = []

    # Check total duration limit
    if total_duration > rules["max_total_third_party_secs"]:
        violations.append(
            f"Total third-party footage exceeds limit: {total_duration:.1f}s > {rules['max_total_third_party_secs']}s"
        )

    # Check transformation ratio
    transform_ratio = overlay_count / max(total_clips, 1)
    if transform_ratio < rules["min_transform_ratio"]:
        violations.append(f"Insufficient transformation ratio: {transform_ratio:.2f} < {rules['min_transform_ratio']}")

    # Check overlay percentage
    overlay_pct = commentary_secs / max(total_duration, 1e-6)
    if overlay_pct < rules["require_overlay_pct"]:
        violations.append(f"Insufficient commentary overlay: {overlay_pct:.2f} < {rules['require_overlay_pct']}")

    return violations


def analyze_timeline(manifest_path: str, rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze timeline manifest for compliance with usage rules.

    Args:
        manifest_path: Path to timeline manifest JSON file
        rules: Optional custom compliance rules

    Returns:
        Dict containing compliance analysis results
    """
    if rules is None:
        rules = DEFAULT_RULES

    manifest_data = _load_manifest_data(manifest_path)

    if not manifest_data.get("uses_third_party"):
        return {
            "compliance_ok": True,
            "notes": ["No third-party footage used."],
            "summary": {},
        }

    segments: List[Dict[str, Any]] = manifest_data.get("segments", [])
    total_third = 0.0
    with_overlay = 0
    commentary_secs = 0.0
    all_violations: List[str] = []

    # Process each third-party segment
    for i, segment in enumerate(segments):
        if segment.get("type") != "third_party":
            continue

        result = _process_segment_compliance(i, segment, rules)

        total_third += result["duration"]
        commentary_secs += result["commentary_secs"]
        all_violations.extend(result["violations"])

        if result["has_overlay"]:
            with_overlay += 1

    # Validate aggregate compliance
    total_clips = len([s for s in segments if s.get("type") == "third_party"])
    aggregate_violations = _validate_aggregate_compliance(
        total_third, with_overlay, total_clips, commentary_secs, rules
    )
    all_violations.extend(aggregate_violations)

    # Calculate final metrics
    transform_ratio = with_overlay / max(total_clips, 1)
    overlay_pct = commentary_secs / max(total_third, 1e-6)

    return {
        "compliance_ok": len(all_violations) == 0,
        "violations": all_violations,
        "summary": {
            "total_third_party_secs": total_third,
            "clips_with_overlay": with_overlay,
            "total_clips": total_clips,
            "transform_ratio": transform_ratio,
            "commentary_secs": commentary_secs,
            "overlay_percentage": overlay_pct,
        },
    }
