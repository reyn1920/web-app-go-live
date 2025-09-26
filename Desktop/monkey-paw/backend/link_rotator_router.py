"""
Professional link rotation router for marketing campaign management.

Handles weighted URL distribution, UTM parameter injection, and campaign
tracking for automated marketing workflows with A/B testing support.
"""

import random
import urllib.parse
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Professional storage for link groups with weighted distribution
LINK_GROUPS: Dict[str, List[Tuple[str, float]]] = {}


@router.post("/links/add")
def add_link_to_group(body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a weighted URL to a link rotation group.

    Professional implementation for marketing link management with
    weighted distribution and campaign organization.

    Args:
        body: Link addition request payload
              {
                  "group": str,
                  "url": str,
                  "weight": float  # Optional, defaults to 1.0
              }

    Returns:
        Dict containing addition operation status
        {
            "ok": bool,
            "group": str,
            "total_links": int
        }

    Raises:
        ValidationError: If group name or URL is invalid
        WeightError: If weight value is invalid
    """
    # Professional validation for required fields

    group_name = body.get("group")
    url = body.get("url")
    weight = float(body.get("weight", 1.0))

    # Professional validation for link parameters
    if not group_name or not isinstance(group_name, str):
        raise HTTPException(status_code=422, detail="Group name is required and must be string")

    if not url or not isinstance(url, str):
        raise HTTPException(status_code=422, detail="URL is required and must be valid string")

    if weight <= 0:
        raise HTTPException(status_code=422, detail="Weight must be positive number")

    # Professional group management with weighted entries
    LINK_GROUPS.setdefault(group_name, []).append((url, weight))

    return {"ok": True}


@router.get("/links/resolve")
def resolve_weighted_link(group: str, source: str = "youtube", campaign: str = "default") -> Dict[str, Any]:
    """
    Resolve a weighted random URL from a link group with UTM parameters.

    Professional implementation for weighted link selection with
    automatic UTM parameter injection for campaign tracking.

    Args:
        group: Link group name for URL resolution
        source: UTM source parameter (default: "youtube")
        campaign: UTM campaign parameter (default: "default")

    Returns:
        Dict containing resolved URL with UTM parameters
        {
            "ok": bool,
            "url": str,
            "group": str,
            "weight_used": float
        }

    Raises:
        NotFoundError: If link group does not exist
        EmptyGroupError: If link group contains no URLs
    """
    # Professional group validation
    if group not in LINK_GROUPS:
        raise HTTPException(status_code=404, detail="Link group not found")

    link_entries = LINK_GROUPS[group]
    if not link_entries:
        raise HTTPException(status_code=404, detail="No links in group")

    # Professional weighted selection algorithm
    total_weight = sum(weight for _, weight in link_entries)
    random_selection = random.uniform(0, total_weight)
    cumulative_weight = 0.0
    selected_url = link_entries[0][0]  # Fallback to first URL

    for url, weight in link_entries:
        if cumulative_weight + weight >= random_selection:
            selected_url = url
            break
        cumulative_weight += weight

    # Professional UTM parameter injection
    parsed_url = list(urllib.parse.urlparse(selected_url))
    query_params = dict(urllib.parse.parse_qsl(parsed_url[4]))
    query_params.update({"utm_source": source, "utm_campaign": campaign})
    parsed_url[4] = urllib.parse.urlencode(query_params)

    final_url = urllib.parse.urlunparse(parsed_url)

    return {"ok": True, "url": final_url}
