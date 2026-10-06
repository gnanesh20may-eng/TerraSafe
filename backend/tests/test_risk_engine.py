from __future__ import annotations

import pytest
from backend.app.config import get_risk_level, get_risk_color, check_false_alarm, get_alert_confidence
from backend.app.alerts.notifications import render_message


def test_risk_levels():
    assert get_risk_level(0) == "LOW"
    assert get_risk_level(24) == "LOW"
    assert get_risk_level(25) == "WATCH"
    assert get_risk_level(49) == "WATCH"
    assert get_risk_level(50) == "HIGH"
    assert get_risk_level(74) == "HIGH"
    assert get_risk_level(75) == "CRITICAL"
    assert get_risk_level(100) == "CRITICAL"


def test_risk_colors():
    assert get_risk_color("LOW") == "#16a34a"
    assert get_risk_color("WATCH") == "#f59e0b"
    assert get_risk_color("HIGH") == "#f97316"
    assert get_risk_color("CRITICAL") == "#dc2626"


def test_false_alarm_rule():
    # Below critical
    res_low = check_false_alarm(50, 1)
    assert res_low["passes"] is True

    # Critical with 1 factor (fails min 2)
    res_crit_1 = check_false_alarm(85, 1)
    assert res_crit_1["passes"] is False

    # Critical with 2 factors (passes)
    res_crit_2 = check_false_alarm(85, 2)
    assert res_crit_2["passes"] is True


def test_alert_confidence():
    conf = get_alert_confidence(80, 2, "LIVE")
    assert 0.5 <= conf <= 0.95


def test_bilingual_warning_text():
    msg_en = render_message("en", "CRITICAL", "Nilgiris")
    assert "CRITICAL" in msg_en or "Critical" in msg_en

    msg_ta = render_message("ta", "CRITICAL", "Nilgiris")
    assert len(msg_ta) > 0
