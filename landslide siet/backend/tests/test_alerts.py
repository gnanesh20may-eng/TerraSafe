from __future__ import annotations

from backend.app.alert_engine import AlertEngine, alert_engine, classify_risk_level


def test_risk_transition_creates_alert_event():
    engine = AlertEngine()
    result = engine.generate_alert(62, previous_level="WATCH")
    assert result["risk_state"] == "HIGH"
    assert result["alert_state"] == "NEW"
    assert result["event"]["previous_state"] == "WATCH"
    assert result["event"]["next_state"] == "HIGH"


def test_low_risk_does_not_trigger_transition_event():
    engine = AlertEngine()
    result = engine.generate_alert(18, previous_level="LOW")
    assert result["risk_state"] == "LOW"
    assert result["alert_state"] == "ACTIVE"


def test_classification_levels_match_thresholds():
    assert classify_risk_level(0) == "LOW"
    assert classify_risk_level(25) == "WATCH"
    assert classify_risk_level(50) == "HIGH"
    assert classify_risk_level(90) == "CRITICAL"
