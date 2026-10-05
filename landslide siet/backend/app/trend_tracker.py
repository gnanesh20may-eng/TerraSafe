from __future__ import annotations
from typing import Any, Dict, List


class TrendTracker:
    def __init__(self):
        self.history = [
            {"time": "06:00", "risk": 32},
            {"time": "09:00", "risk": 41},
            {"time": "12:00", "risk": 58},
            {"time": "15:00", "risk": 74},
            {"time": "18:00", "risk": 87},
        ]

    def get_trend(self, current: int | None = None):
        if current is not None:
            return [{"time": item["time"], "risk": item["risk"]} for item in self.history[:-1]] + [{"time": "Now", "risk": current}]
        return self.history


trend_tracker = TrendTracker()
