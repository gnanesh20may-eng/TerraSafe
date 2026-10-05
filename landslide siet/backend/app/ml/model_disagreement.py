from __future__ import annotations

import math
from typing import Any


def assess_model_disagreement(probabilities: dict[str, float], threshold: float = 0.2) -> dict[str, Any]:
    if not math.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("disagreement threshold must be in [0, 1]")
    if len(probabilities) < 2:
        return {"available": False, "disagreement": None, "spread": None, "models": sorted(probabilities)}
    values = list(probabilities.values())
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in values):
        raise ValueError("model probabilities must be finite and in [0, 1]")
    spread = max(values) - min(values)
    return {
        "available": True,
        "disagreement": spread >= threshold,
        "spread": spread,
        "threshold": threshold,
        "models": sorted(probabilities),
    }
