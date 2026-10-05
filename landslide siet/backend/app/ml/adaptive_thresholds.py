from __future__ import annotations

import math
from typing import Any


def estimate_zone_threshold(
    historical_scores: list[float],
    *,
    quantile: float = 0.9,
    minimum_samples: int = 30,
    fallback_threshold: float = 50.0,
) -> dict[str, Any]:
    if not 0 < quantile < 1 or minimum_samples < 2:
        raise ValueError("quantile and minimum_samples are invalid")
    if not math.isfinite(fallback_threshold) or not 0 <= fallback_threshold <= 100:
        raise ValueError("fallback threshold must be in [0, 100]")
    if any(not math.isfinite(score) or not 0 <= score <= 100 for score in historical_scores):
        raise ValueError("historical scores must be finite and in [0, 100]")
    if len(historical_scores) < minimum_samples:
        return {
            "threshold": fallback_threshold,
            "source": "DEMO DEFAULT",
            "calibrated": False,
            "sample_count": len(historical_scores),
        }

    ordered = sorted(historical_scores)
    position = quantile * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    threshold = ordered[lower] * (1 - fraction) + ordered[upper] * fraction
    return {
        "threshold": threshold,
        "source": "EXPERIMENTAL EMPIRICAL QUANTILE",
        "calibrated": False,
        "sample_count": len(ordered),
    }
