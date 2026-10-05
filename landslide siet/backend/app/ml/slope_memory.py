from __future__ import annotations

import math


def cumulative_slope_memory(stress_values_newest_first: list[float], decay_periods: float) -> float:
    if decay_periods <= 0 or not math.isfinite(decay_periods):
        raise ValueError("decay_periods must be finite and positive")
    if any(not math.isfinite(value) or value < 0 for value in stress_values_newest_first):
        raise ValueError("stress values must be finite and non-negative")
    return sum(value * math.exp(-age / decay_periods) for age, value in enumerate(stress_values_newest_first))
