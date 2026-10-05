from typing import Any, Dict, List


def classify_risk(score: float) -> str:
    if score <= 25:
        return "LOW"
    if score <= 50:
        return "MODERATE"
    if score <= 75:
        return "HIGH"
    return "CRITICAL"


def get_risk_color(level: str) -> str:
    mapping = {"LOW": "#22c55e", "MODERATE": "#facc15", "HIGH": "#f97316", "CRITICAL": "#ef4444"}
    return mapping.get(level.upper(), "#94a3b8")
