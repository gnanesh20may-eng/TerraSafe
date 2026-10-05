from __future__ import annotations

import hashlib
import json
import logging
from datetime import date

from scripts import download_all


def test_open_meteo_request_is_single_point_and_one_week():
    registry = download_all.load_registry()
    source = next(item for item in registry["sources"] if item["id"] == "open_meteo_nilgiris_history")

    url, params, label = download_all.build_request(source, "nilgiris", registry)

    assert url == "https://archive-api.open-meteo.com/v1/archive"
    assert params["latitude"] == 11.35
    assert params["longitude"] == 76.8
    assert params["hourly"] == "precipitation,soil_moisture_0_to_7cm"
    start_date, end_date = label.split("_")
    assert (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days == 6


def test_mock_writer_marks_fixture_simulated_and_never_live(tmp_path, monkeypatch):
    monkeypatch.setattr(download_all, "ROOT", tmp_path)
    logger = logging.getLogger("test-downloader")
    source = {"id": "sensor_simulator"}

    path = download_all.write_mock(source, "nilgiris", logger)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["status"] == "SIMULATED"
    assert payload["synthetic"] is True
    assert payload["records"] == []


def test_streamed_download_writes_checksum_sidecar(tmp_path, monkeypatch):
    class MockResponse:
        status_code = 200
        headers = {"content-length": "7"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def raise_for_status(self):
            return None

        def iter_bytes(self, _chunk_size):
            yield b"data"
            yield b"123"

    class MockClient:
        def __init__(self, **_kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def stream(self, *_args, **_kwargs):
            return MockResponse()

    monkeypatch.setattr(download_all.httpx, "Client", MockClient)
    target = tmp_path / "sample.json"

    digest = download_all.download("https://example.test/source", {}, target, False, logging.getLogger("test"))

    assert target.read_bytes() == b"data123"
    assert digest == hashlib.sha256(b"data123").hexdigest()
    assert target.with_suffix(".json.sha256").read_text(encoding="ascii").startswith(digest)
