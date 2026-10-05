from backend.app.gis.risk_zones import RiskSignals, calculate_risk_score, build_risk_zone_geojson


def test_calculate_risk_score_ranges_and_levels():
    signals = RiskSignals(
        rainfall_24h_mm=75,
        rainfall_7d_mm=180,
        soil_moisture_pct=72,
        slope_deg=35,
        ndvi=0.3,
        elevation_m=1800,
        historical_landslides_nearby=2,
    )
    result = calculate_risk_score(signals)
    assert 0 <= result["score"] <= 100
    assert result["level"] in {"HIGH", "CRITICAL"}
    assert "Heavy 24-hour rainfall" in result["reasons"]


def test_geojson_zone_has_polygon_and_metadata():
    locations = [{"id": "coonor", "name": "Coonoor", "latitude": 11.35, "longitude": 76.8}]
    geojson = build_risk_zone_geojson(locations, {"coonor": 68})
    assert geojson["type"] == "FeatureCollection"
    assert geojson["features"][0]["geometry"]["type"] == "Polygon"
    assert "Synthetic demonstration output" in geojson["metadata"]["disclaimer"]


def test_low_risk_is_classified_as_low():
    signals = RiskSignals(
        rainfall_24h_mm=10,
        rainfall_7d_mm=30,
        soil_moisture_pct=35,
        slope_deg=8,
        ndvi=0.8,
        elevation_m=500,
        historical_landslides_nearby=0,
    )
    result = calculate_risk_score(signals)
    assert result["level"] == "LOW"
