from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Optional

RiskLevel = Literal["LOW", "WATCH", "HIGH", "CRITICAL"]
AlertState = Literal["NEW", "ACKNOWLEDGED", "ACTIVE", "RESOLVED"]


def classify_risk_level(score: float) -> RiskLevel:
    if score < 25:
        return "LOW"
    if score < 50:
        return "WATCH"
    if score < 75:
        return "HIGH"
    return "CRITICAL"


@dataclass
class AlertEvent:
    previous_state: Optional[RiskLevel]
    next_state: RiskLevel
    alert_state: AlertState
    message: str
    timestamp: str


class RiskStateMachine:
    def __init__(self) -> None:
        self.history: list[AlertEvent] = []

    def transition(self, previous_state: Optional[RiskLevel], next_state: RiskLevel, message: str) -> AlertEvent:
        if previous_state == next_state:
            event = AlertEvent(previous_state, next_state, "ACTIVE", message, self._utc_now())
            self.history.append(event)
            return event

        event = AlertEvent(previous_state, next_state, "NEW", f"{previous_state or 'UNKNOWN'} -> {next_state}: {message}", self._utc_now())
        self.history.append(event)
        return event

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class AlertEngine:
    def __init__(self) -> None:
        self.state_machine = RiskStateMachine()

    def generate_alert(self, score: float, previous_level: Optional[RiskLevel] = None) -> dict:
        level = classify_risk_level(score)
        message = self._build_message(level)
        event = self.state_machine.transition(previous_level, level, message)
        alert_state = event.alert_state
        if previous_level is None:
            alert_state = "NEW"
        elif previous_level == level:
            alert_state = "ACTIVE"

        return {
            "risk_state": level,
            "alert_state": alert_state,
            "message": message,
            "event": {
                "previous_state": event.previous_state,
                "next_state": event.next_state,
                "alert_state": event.alert_state,
                "message": event.message,
                "timestamp": event.timestamp,
            },
        }

    @staticmethod
    def _build_message(level: RiskLevel) -> str:
        mapping = {
            "LOW": "Conditions are currently stable. Continue monitoring local weather and official guidance.",
            "WATCH": "Elevated rainfall and soil moisture indicate increased monitoring needs.",
            "HIGH": "Risk is elevated. Avoid unnecessary travel through steep or vulnerable areas.",
            "CRITICAL": "Very high risk conditions detected. Follow local authorities and designated safety guidance.",
        }
        return mapping[level]


alert_engine = AlertEngine()
