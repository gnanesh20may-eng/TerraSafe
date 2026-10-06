"""Unified configuration for TerraSafe risk thresholds and feature flags."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class RiskThresholds(BaseModel):
    """Risk level thresholds (0-100 scale)."""
    low_max: int = Field(default=24, ge=0, le=100)
    watch_max: int = Field(default=49, ge=0, le=100)
    high_max: int = Field(default=74, ge=0, le=100)
    # critical is 75-100

    def get_level(self, score: int) -> str:
        if score <= self.low_max:
            return "LOW"
        if score <= self.watch_max:
            return "WATCH"
        if score <= self.high_max:
            return "HIGH"
        return "CRITICAL"

    def get_color(self, level: str) -> str:
        colors = {
            "LOW": "#16a34a",
            "WATCH": "#f59e0b",
            "HIGH": "#f97316",
            "CRITICAL": "#dc2626",
        }
        return colors.get(level, "#6b7280")


class FalseAlarmConfig(BaseModel):
    """False alarm prevention configuration."""
    critical_min_supporting_factors: int = Field(default=2, ge=1, le=5)
    confidence_threshold: float = Field(default=0.7, ge=0.5, le=0.95)


class AlertStateConfig(BaseModel):
    """Alert lifecycle states."""
    states: list[str] = Field(default=[
        "NEW",
        "ACKNOWLEDGED",
        "ACTIVE",
        "RESOLVED"
    ])
    transitions: dict[str, str] = Field(default={
        "NEW": "ACKNOWLEDGED",
        "ACKNOWLEDGED": "ACTIVE",
        "ACTIVE": "RESOLVED",
    })


class VulnerablePriorityConfig(BaseModel):
    """Vulnerable location priority scoring."""
    priority_1_threshold: float = Field(default=0.8, ge=0.5, le=1.0)
    priority_2_threshold: float = Field(default=0.6, ge=0.3, le=0.8)
    priority_3_threshold: float = Field(default=0.4, ge=0.0, le=0.6)

    def get_priority(self, risk_score: float) -> int:
        if risk_score >= self.priority_1_threshold:
            return 1
        if risk_score >= self.priority_2_threshold:
            return 2
        if risk_score >= self.priority_3_threshold:
            return 3
        return 0


class AppConfig(BaseModel):
    """Main application configuration."""
    risk_thresholds: RiskThresholds = Field(default_factory=RiskThresholds)
    false_alarm: FalseAlarmConfig = Field(default_factory=FalseAlarmConfig)
    alert_states: AlertStateConfig = Field(default_factory=AlertStateConfig)
    vulnerable_priority: VulnerablePriorityConfig = Field(default_factory=VulnerablePriorityConfig)

    # Feature flags
    enable_copilot: bool = True
    enable_what_if_simulator: bool = True
    enable_counterfactuals: bool = True

    # External API keys (set via env)
    open_meteo_timeout: float = 5.0
    usgs_timeout: float = 5.0
    nasa_timeout: float = 5.0


# Global config instance
config = AppConfig()


def get_risk_level(score: int) -> str:
    """Get risk level from 0-100 score."""
    return config.risk_thresholds.get_level(score)


def get_risk_color(level: str) -> str:
    """Get color for risk level."""
    return config.risk_thresholds.get_color(level)


def check_false_alarm(score: int, supporting_factors: int) -> dict[str, Any]:
    """Check if a CRITICAL alert passes the false-alarm rule."""
    if score < config.risk_thresholds.high_max + 1:  # Not CRITICAL
        return {"passes": True, "reason": "Not CRITICAL level"}

    min_factors = config.false_alarm.critical_min_supporting_factors
    if supporting_factors >= min_factors:
        return {"passes": True, "reason": f"Has {supporting_factors} supporting factors (min {min_factors})"}
    return {
        "passes": False,
        "reason": f"CRITICAL requires {min_factors} supporting factors, got {supporting_factors}"
    }


def get_alert_confidence(score: int, supporting_factors: int, data_quality: str = "LIVE") -> float:
    """Calculate alert confidence based on score, factors, and data quality."""
    base_confidence = score / 100.0
    factor_boost = min(supporting_factors * 0.05, 0.2)
    quality_multiplier = {
        "LIVE": 1.0,
        "SIMULATED": 0.7,
        "HISTORICAL": 0.8,
        "DEMO": 0.5,
    }.get(data_quality, 0.5)

    confidence = (base_confidence + factor_boost) * quality_multiplier
    return round(min(confidence, 0.95), 2)


def get_alert_state_transitions() -> dict[str, str]:
    """Get valid alert state transitions."""
    return config.alert_states.transitions


def get_vulnerable_priority(risk_score: float) -> int:
    """Get vulnerable location priority (1=highest, 3=lowest, 0=none)."""
    return config.vulnerable_priority.get_priority(risk_score)