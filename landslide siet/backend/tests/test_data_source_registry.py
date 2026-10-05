from __future__ import annotations

from backend.app.api.v1 import routes
from scripts.download_all import load_registry


def test_registry_has_ten_regions_and_complete_source_metadata():
    registry = load_registry()
    required = {
        "id", "name", "category", "url", "access", "format",
        "update_frequency", "license", "region_coverage", "fallback",
        "target_path", "status",
    }

    assert len(registry["regions"]) == 10
    assert len(registry["sources"]) >= 40
    assert all(required <= set(source) for source in registry["sources"])
    assert all(len(region["bbox"]) == 4 for region in registry["regions"].values())


def test_unclear_nasa_catalog_endpoint_stays_out_of_automated_downloads():
    sources = {source["id"]: source for source in load_registry()["sources"]}

    assert sources["nasa_global_landslide_catalog"]["status"] == "needs_review"
    assert "adapter" not in sources["nasa_global_landslide_catalog"]


def test_data_health_endpoint_is_explicit_before_a_check_runs(monkeypatch, tmp_path):
    monkeypatch.setattr(routes, "DATA_HEALTH_PATH", tmp_path / "missing.json")

    result = routes.health_data_sources()

    assert result["status"] == "NEEDS_REVIEW"
    assert result["sources"] == []


def test_data_health_endpoint_returns_saved_source_snapshot(monkeypatch, tmp_path):
    health_path = tmp_path / "health.json"
    health_path.write_text(
        '{"region":"nilgiris","sources":[{"id":"usgs_earthquake_catalog","status":"WORKING"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(routes, "DATA_HEALTH_PATH", health_path)

    result = routes.health_data_sources()

    assert result["sources"][0]["status"] == "WORKING"
