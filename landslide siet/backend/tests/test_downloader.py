from datetime import datetime, timezone

import pytest

from scripts.download_all import build_request, download


def test_nilgiris_open_meteo_download_is_bounded_historical_json():
    url, params = build_request(
        "open_meteo_archive",
        "nilgiris",
        datetime(2026, 10, 5, tzinfo=timezone.utc),
    )

    assert url == "https://archive-api.open-meteo.com/v1/archive"
    assert params["hourly"] == "precipitation,soil_moisture_0_to_7cm"
    assert params["start_date"] == "2026-09-22"
    assert params["end_date"] == "2026-09-28"
    assert params["latitude"] == 11.35


def test_mock_download_is_explicit_and_checksummed(tmp_path):
    result = download("usgs_earthquakes", "nilgiris", tmp_path / "usgs.json", mock=True)
    output = tmp_path / "usgs.mock.json"

    assert result["mock"] is True
    assert output.exists()
    assert output.with_suffix(output.suffix + ".sha256").exists()
    assert '"synthetic": true' in output.read_text(encoding="utf-8")


def test_downloader_refuses_unverified_sources_and_unknown_regions():
    with pytest.raises(ValueError, match="No verified open downloader"):
        build_request("nasa_global_landslide_catalog", "nilgiris")
    with pytest.raises(ValueError, match="Unknown region"):
        build_request("usgs_earthquakes", "not-a-region")