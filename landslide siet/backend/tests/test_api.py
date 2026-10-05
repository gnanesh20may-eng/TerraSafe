# API Integration Tests
# Run with: pytest backend/tests/test_api.py -v

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "disclaimer" in data


class TestRiskAPI:
    def test_risk_api_basic(self):
        response = client.get("/api/risk?lat=11.4064&lon=76.6932")
        assert response.status_code == 200
        data = response.json()
        assert "riskScore" in data
        assert "riskLevel" in data
        assert "location" in data
        assert 0 <= data["riskScore"] <= 100

    def test_risk_api_valid_levels(self):
        response = client.get("/api/risk?lat=11.4064&lon=76.6932")
        assert response.status_code == 200
        data = response.json()
        assert data["riskLevel"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]

    def test_risk_api_includes_sources(self):
        response = client.get("/api/risk?lat=11.4064&lon=76.6932")
        assert response.status_code == 200
        data = response.json()
        assert "source_status" in data
        assert "demoMode" in data


class TestZonesAPI:
    def test_zones_list(self):
        response = client.get("/api/zones")
        assert response.status_code == 200
        data = response.json()
        assert "zones" in data
        assert len(data["zones"]) == 4

    def test_zone_detail(self):
        response = client.get("/api/zones/Zone%20A")
        assert response.status_code in [200, 404]  # Zone name may vary


class TestSimulationAPI:
    def test_simulation_basic(self):
        response = client.post(
            "/api/simulation?zone=Ooty&rainfall=150&soil_moisture=75&slope=35"
        )
        assert response.status_code == 200
        data = response.json()
        assert "current" in data
        assert 0 <= data["current"] <= 100
        assert data["risk_level"] in ["LOW", "MODERATE", "HIGH", "CRITICAL"]


class TestCopilotAPI:
    def test_copilot_question(self):
        response = client.get(
            "/api/copilot?question=Which%20zones%20are%20critical"
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] is not None
        assert len(data["answer"]) > 0


class TestTrendsAPI:
    def test_trends_endpoint(self):
        response = client.get("/api/trends")
        assert response.status_code == 200
        data = response.json()
        assert "trend" in data
        assert "current" in data


class TestVulnerableLocationsAPI:
    def test_vulnerable_locations(self):
        response = client.get("/api/vulnerable-locations")
        assert response.status_code == 200
        data = response.json()
        assert "Priority 1" in data or "zones" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
