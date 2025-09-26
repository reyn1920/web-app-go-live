"""
A/B testing router: provides endpoints for variant selection and reporting using UCB.
"""

import math
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

router = APIRouter()

# Global experiments storage: name -> {variant -> stats}
EXPERIMENTS: Dict[str, Dict[str, Dict[str, Any]]] = {}


@router.post("/ab/choose")
def choose_variant(body: Dict[str, Any]) -> Dict[str, Any]:
    """Choose optimal variant using Upper Confidence Bound algorithm."""

    experiment_name = str(body.get("name", ""))

    variants: list[str] = []
    variants_raw = body.get("variants")

    def extract_variants(val: Any) -> list[str]:
        if isinstance(val, list):
            from typing import cast

            return [str(v) for v in cast(list[Any], val) if isinstance(v, (str, int, float))]
        if isinstance(val, str):
            return [val]
        return []

    variants = extract_variants(variants_raw)

    if not experiment_name or not variants:
        raise HTTPException(status_code=400, detail="name and variants are required")

    experiment = EXPERIMENTS.setdefault(experiment_name, {})
    total_shows = sum(max(stats.get("shows", 0), 1) for stats in experiment.values()) or 1

    def ucb_score_fn(variant: str) -> float:
        stats = experiment.setdefault(variant, {"shows": 0, "rewards": 0.0})
        shows = stats["shows"]
        avg_reward = (stats["rewards"] / shows) if shows > 0 else 0.0
        exploration_bonus = math.sqrt(2 * math.log(total_shows) / max(shows, 1))
        return avg_reward + exploration_bonus

    best_variant = max(variants, key=ucb_score_fn)
    return {"ok": True, "variant": best_variant}


@router.post("/ab/report")
def report_result(body: Dict[str, Any]) -> Dict[str, Any]:
    """Report A/B test result for a specific variant."""
    experiment_name = body.get("name", "")
    variant = body.get("variant", "")
    reward = float(body.get("reward", 0.0))

    if not experiment_name or not variant:
        raise HTTPException(status_code=400, detail="name and variant are required")

    stats = EXPERIMENTS.setdefault(experiment_name, {}).setdefault(variant, {"shows": 0, "rewards": 0.0})
    stats["shows"] += 1
    stats["rewards"] += reward

    return {"ok": True}
