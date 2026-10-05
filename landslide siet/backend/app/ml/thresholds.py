from __future__ import annotations

from collections.abc import Iterable

import numpy as np


class AdaptiveZoneThresholds:
    def __init__(self, default: float = 0.5, minimum: float = 0.25, maximum: float = 0.8):
        if not 0 <= minimum <= default <= maximum <= 1:
            raise ValueError("threshold bounds must satisfy 0 <= minimum <= default <= maximum <= 1")
        self.default = default
        self.minimum = minimum
        self.maximum = maximum

    def for_zone(self, zone: str, historical_scores: Iterable[float] = ()) -> float:
        scores = np.asarray(list(historical_scores), dtype=float)
        if scores.size:
            if np.any((scores < 0) | (scores > 1)):
                raise ValueError("historical scores must be probabilities in [0, 1]")
            candidate = float(np.quantile(scores, 0.8))
        else:
            offsets = {"high": -0.05, "critical": -0.1, "watch": 0.0, "low": 0.05}
            candidate = self.default + offsets.get(zone.lower(), 0.0)
        return min(self.maximum, max(self.minimum, candidate))