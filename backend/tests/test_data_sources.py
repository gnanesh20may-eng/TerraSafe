import asyncio
import hashlib
import io
import json
from datetime import date
from pathlib import Path

import httpx
import pytest

from backend.app import data_sources
from backend.app.data_sources import inspect_observations, load_source_registry
from backend.app.main import app
from scripts import download_all
from scripts import check_sources


def test_registry_contains_complete_entries_and_marks_uncertainty():
    sources = load_source_registry()

    assert len(sources) >= 40
    assert len({source["id"] for source in sources}) == len(sources)
    assert all(data_sources.REGISTRY_FIELDS <= source.keys() for source in sources)
    assert {source["status"] for source in sources} <= data_sources.HEALTH_STATUSES
    assert all(source["licence"] for source in sources)


def test_source_health_endpoint_returns_registry_status_without_live_claims(
    monkeypatch, tmp_path
):
    report_path = tmp_path / "source_health.json"
    monkeypatch.setattr(data_sources, "HEALTH_PATH", report_path)

    async def request_health():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://terrasafe.test"
        ) as client:
            return await client.get("/api/v1/health/data-sources")

    response = asyncio.run(request_health())

    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 40
    assert len(body["sources"]) == body["count"]
    assert {source["status"] for source in body["sources"]} <= {
        "MANUAL",
        "NEEDS_REVIEW",
    }
    assert all(source["checked_at"] is None for source in body["sources"])

    report_path.write_text(
        json.dumps(
            {
                "sources": [
                    {
                        "id": "usgs_earthquakes",
                        "status": "WORKING",
                        "checked_at": "2026-10-05T00:00:00+00:00",
                        "detail": "HTTP 200; JSON object response received.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    updated = asyncio.run(request_health()).json()
    usgs = next(row for row in updated["sources"] if row["id"] == "usgs_earthquakes")
    assert usgs["status"] == "WORKING"
    assert usgs["checked_at"] == "2026-10-05T00:00:00+00:00"


def test_quality_report_detects_nulls_duplicates_label_balance_and_leakage():
    report = inspect_observations(
        [
            {
                "longitude": 76.7,
                "latitude": 11.35,
                "label": 0,
                "spatial_group": "cell-a",
                "fold": 0,
                "soil": None,
            },
            {
                "longitude": 76.7,
                "latitude": 11.35,
                "label": 0,
                "spatial_group": "cell-a",
                "fold": 0,
                "soil": None,
            },
            {
                "longitude": 76.8,
                "latitude": 11.4,
                "label": 1,
                "spatial_group": "cell-b",
                "fold": 1,
                "soil": 0.4,
            },
            {
                "longitude": 181,
                "latitude": 91,
                "label": 1,
                "spatial_group": "cell-b",
                "fold": 2,
                "soil": 0.5,
            },
        ],
        label_column="label",
        group_column="spatial_group",
        fold_column="fold",
    )

    assert report["row_count"] == 4
    assert report["crs"] == "NOT_PROVIDED"
    assert report["crs_status"] == "NOT_PROVIDED"
    assert report["coordinate_range_check_crs"] == "EPSG:4326"
    assert report["coordinate_errors"] == [
        {"row": 3, "field": "longitude"},
        {"row": 3, "field": "latitude"},
    ]
    assert report["null_counts"]["soil"] == 2
    assert report["duplicate_rows"] == 1
    assert report["label_balance"] == {"0": 2, "1": 2}
    assert report["spatial_leakage"]["leaking_groups"] == ["cell-b"]


def test_quality_report_handles_empty_rows_and_unchecked_spatial_split():
    report = inspect_observations([])

    assert report["row_count"] == 0
    assert report["coordinate_errors"] == []
    assert report["spatial_leakage"]["checked"] is False
    assert inspect_observations([], source_crs="EPSG:3857")["crs_status"] == "MISMATCH"
    assert inspect_observations([], source_crs="EPSG:4326")["crs_status"] == "MATCH"


def test_download_request_is_nilgiris_scoped_and_has_requested_date_range():
    url, extension = download_all.build_request(
        "open_meteo_archive",
        "Nilgiris",
        date(2025, 1, 1),
        date(2025, 1, 2),
    )

    assert "start_date=2025-01-01" in url
    assert "end_date=2025-01-02" in url
    assert extension == ".json"
    with pytest.raises(ValueError, match="only for Nilgiris"):
        download_all.build_request(
            "usgs_earthquakes",
            "Kerala Ghats",
            date(2025, 1, 1),
            date(2025, 1, 2),
        )
    with pytest.raises(ValueError, match="not an implemented"):
        download_all.build_request(
            "nasa_global_landslide_catalog",
            "Nilgiris",
            date(2025, 1, 1),
            date(2025, 1, 2),
        )


def test_bounded_download_writes_checksum_and_uses_part_file(tmp_path, monkeypatch):
    content = b'{"observed": true}'

    class FakeResponse(io.BytesIO):
        status = 200
        headers = {"Content-Length": str(len(content))}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(download_all, "urlopen", lambda *_args, **_kwargs: FakeResponse(content))
    destination = tmp_path / "download.json"

    checksum = download_all.fetch_bounded("https://data.example.test/", destination, resume=False)

    assert destination.read_bytes() == content
    assert checksum == hashlib.sha256(content).hexdigest()
    assert not Path(str(destination) + ".part").exists()


def test_bounded_download_rejects_oversized_response(tmp_path, monkeypatch):
    class FakeResponse(io.BytesIO):
        status = 200
        headers = {"Content-Length": "5"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(download_all, "MAX_DOWNLOAD_BYTES", 4)
    monkeypatch.setattr(download_all, "urlopen", lambda *_args, **_kwargs: FakeResponse(b"12345"))

    with pytest.raises(ValueError, match="200 MiB"):
        download_all.fetch_bounded(
            "https://data.example.test/", tmp_path / "oversized.json", resume=False
        )
    assert not (tmp_path / "oversized.json").exists()
    assert not (tmp_path / "oversized.json.part").exists()


def test_bounded_download_resumes_and_sends_range_header(tmp_path, monkeypatch):
    content = b'{"resume": true}'
    partial_content = content[:5]
    remaining = content[5:]
    destination = tmp_path / "resumed.json"
    Path(str(destination) + ".part").write_bytes(partial_content)
    captured = {}

    class FakeResponse(io.BytesIO):
        status = 206
        headers = {"Content-Length": str(len(remaining))}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    def fake_urlopen(request, **_kwargs):
        captured.update(request.header_items())
        return FakeResponse(remaining)

    monkeypatch.setattr(download_all, "urlopen", fake_urlopen)

    checksum = download_all.fetch_bounded("https://data.example.test/", destination, resume=True)

    assert captured["Range"] == f"bytes={len(partial_content)}-"
    assert destination.read_bytes() == content
    assert checksum == hashlib.sha256(content).hexdigest()


def test_source_checker_uses_bounded_json_probe_and_manual_status(monkeypatch):
    class FakeResponse(io.BytesIO):
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(
        check_sources,
        "urlopen",
        lambda *_args, **_kwargs: FakeResponse(b'{"hourly":{"time":[]}}'),
    )
    source = next(
        item for item in load_source_registry() if item["id"] == "open_meteo_archive"
    )
    checked = check_sources.check_source(source, "Nilgiris")

    assert checked["status"] == "WORKING"
    assert "JSON object" in checked["detail"]

    manual = next(item for item in load_source_registry() if item["id"] == "gsi_bhukosh")
    monkeypatch.setattr(
        check_sources,
        "urlopen",
        lambda *_args, **_kwargs: pytest.fail("manual source must not be probed"),
    )
    assert check_sources.check_source(manual, "Nilgiris")["status"] == "MANUAL"
