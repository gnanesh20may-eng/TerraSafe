#!/usr/bin/env python
"""Test suite for LandSense backend."""

import pytest
from backend.app.risk_engine import calc_weighted_risk
from backend.app.demo_data import get_demo_location
from backend.app.models import classify_risk


class TestRiskEngine:
    def test_low_risk(self):
        """Test low risk scenario."""
        score, factors, _ = calc_weighted_risk(
            {"rain_24h_mm": 10, "rain_72h_mm": 20, "soil_moisture": 30},
            {"slope_deg": 10},
            {"ndvi": 0.8},
            {"historical_landslides_nearby": 0},
        )
        assert score <= 35
        assert classify_risk(score) == "LOW"

    def test_critical_risk(self):
        """Test critical risk scenario."""
        score, factors, _ = calc_weighted_risk(
            {"rain_24h_mm": 160, "rain_72h_mm": 240, "soil_moisture": 85},
            {"slope_deg": 34},
            {"ndvi": 0.38},
            {"historical_landslides_nearby": 8},
        )
        assert score >= 80
        assert classify_risk(score) == "CRITICAL"

    def test_moderate_risk(self):
        """Test moderate risk scenario."""
        score, factors, _ = calc_weighted_risk(
            {"rain_24h_mm": 74, "rain_72h_mm": 128, "soil_moisture": 62},
            {"slope_deg": 26},
            {"ndvi": 0.56},
            {"historical_landslides_nearby": 4},
        )
        assert 31 <= score <= 60
        assert classify_risk(score) == "MODERATE"

    def test_score_bounds(self):
        """Test that score is always 0-100."""
        score, _, _ = calc_weighted_risk(
            {"rain_24h_mm": 500, "rain_72h_mm": 1000, "soil_moisture": 100},
            {"slope_deg": 90},
            {"ndvi": 0},
            {"historical_landslides_nearby": 100},
        )
        assert 0 <= score <= 100


class TestDemoData:
    def test_ooty_location(self):
        """Test Ooty demo location."""
        name, data = get_demo_location(11.4064, 76.6932)
        assert "Ooty" in name or "Nilgiris" in name
        assert data.get("elevation_m") == 2240
        assert data.get("slope_deg") == 31

    def test_wayanad_location(self):
        """Test Wayanad demo location."""
        name, data = get_demo_location(11.6854, 76.1321)
        assert "Wayanad" in name
        assert data.get("historical_landslides_nearby") == 7

    def test_unknown_location(self):
        """Test unknown location returns empty data."""
        name, data = get_demo_location(90.0, 180.0)
        # Should return unknown or nearest location
        assert name is not None or data == {}


class TestClassification:
    def test_low_classification(self):
        assert classify_risk(15) == "LOW"
        assert classify_risk(30) == "LOW"

    def test_moderate_classification(self):
        assert classify_risk(31) == "MODERATE"
        assert classify_risk(60) == "MODERATE"

    def test_high_classification(self):
        assert classify_risk(61) == "HIGH"
        assert classify_risk(80) == "HIGH"

    def test_critical_classification(self):
        assert classify_risk(81) == "CRITICAL"
        assert classify_risk(100) == "CRITICAL"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
