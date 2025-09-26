"""Endpoints for ingesting manifests (e.g., FCPXML)."""

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from clip_compliance import DEFAULT_RULES, analyze_timeline
from edl_parser import parse_edl
from fastapi import APIRouter, HTTPException
from fcpxml_parser import parse_fcpxml
from manifest_builder import events_to_manifest, load_mapping

router = APIRouter()


def write_and_check(manifest: Dict[str, Any], out_folder: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Write manifest and perform compliance check.

    Args:
        manifest: Manifest data to write
        out_folder: Output directory path

    Returns:
        Tuple of manifest path and compliance results
    """
    out_folder.mkdir(parents=True, exist_ok=True)
    mani_path = out_folder / "timeline.json"
    mani_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    res = analyze_timeline(str(mani_path), DEFAULT_RULES)
    (out_folder / "compliance.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    return str(mani_path), res


@router.post("/compliance/ingest_fcpxml")
def ingest_fcpxml(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest FCPXML file and generate compliance manifest.

    Args:
        body: Request body containing slug, xml_path, and mapping_csv

    Returns:
        Dict containing ingestion results and compliance data
    """
    slug = (body.get("slug") or "").strip()
    xml_path = (body.get("xml_path") or "").strip()
    mapping_csv = (body.get("mapping_csv") or "").strip()

    if not slug or not Path(xml_path).exists():
        raise HTTPException(status_code=400, detail="slug or xml_path missing")

    parsed = parse_fcpxml(xml_path)
    events = parsed["events"]
    from typing import List, cast

    titles = cast(List[Dict[str, float]], parsed.get("titles") or [])
    vo = cast(List[Dict[str, float]], parsed.get("vo_regions") or [])
    mapping = load_mapping(mapping_csv)

    mani = events_to_manifest(events, mapping, slug, title_regions=titles, vo_regions=vo)
    mani_path, comp = write_and_check(mani, Path(f"assets/out/{slug}"))

    return {
        "ok": True,
        "manifest": mani_path,
        "compliance": comp,
        "detected": {"titles": len(titles), "vo_regions": len(vo)},
    }


@router.post("/compliance/ingest_edl")
def ingest_edl(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingest EDL file and generate compliance manifest.

    Args:
        body: Request body containing slug, edl_path, fps, and mapping_csv

    Returns:
        Dict containing ingestion results and compliance data
    """
    slug = (body.get("slug") or "").strip()
    edl_path = (body.get("edl_path") or "").strip()
    fps = int(body.get("fps", 30))
    mapping_csv = (body.get("mapping_csv") or "").strip()

    if not slug or not Path(edl_path).exists():
        raise HTTPException(status_code=400, detail="slug or edl_path missing")

    events = parse_edl(edl_path, fps=fps)
    mapping = load_mapping(mapping_csv)
    mani = events_to_manifest(events, mapping, slug)
    mani_path, comp = write_and_check(mani, Path(f"assets/out/{slug}"))

    return {"ok": True, "manifest": mani_path, "compliance": comp}


@router.post("/compliance/ingest_auto")
def ingest_auto(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Auto-detect and ingest the latest FCPXML or EDL file.

    Args:
        body: Request body containing slug and optional folder

    Returns:
        Dict containing ingestion results
    """
    slug = (body.get("slug") or "").strip()
    folder = Path(body.get("folder") or "assets/inbox")

    if not slug or not folder.exists():
        raise HTTPException(status_code=400, detail="slug or folder missing")

    candidates = sorted(
        list(folder.glob("*.fcpxml")) + list(folder.glob("*.edl")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not candidates:
        raise HTTPException(status_code=404, detail="no .fcpxml or .edl found")

    latest_file = candidates[0]
    default_mapping = "assets/mappings/clip_sources.csv"

    if latest_file.suffix.lower() == ".fcpxml":
        return ingest_fcpxml({"slug": slug, "xml_path": str(latest_file), "mapping_csv": default_mapping})
    else:
        return ingest_edl(
            {
                "slug": slug,
                "edl_path": str(latest_file),
                "mapping_csv": default_mapping,
                "fps": 30,
            }
        )
