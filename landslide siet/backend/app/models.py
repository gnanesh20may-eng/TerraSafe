from typing import Dict, Any, Tuple


def classify_risk(score: int) -> str:
    """Classify risk score into level."""
    if score <= 30:
        return "LOW"
    elif score <= 60:
        return "MODERATE"
    elif score <= 80:
        return "HIGH"
    else:
        return "CRITICAL"
