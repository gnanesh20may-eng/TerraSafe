"""Async JSON ingestion with explicit mock mode, caching, and bounded retries."""

from __future__ import annotations

import asyncio
import copy
import hashlib
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Mapping

import aiohttp


class SourceAdapterError(RuntimeError):
    """A configured data source could not return a valid response."""


@dataclass(frozen=True)
class SourceSnapshot:
    source: str
    fetched_at: str
    payload: dict[str, Any]
    is_mock: bool
    cache_hit: bool


class AsyncJSONIngestor:
    """Fetch JSON from an endpoint or return a clearly marked local fixture."""

    def __init__(
        self,
        source: str,
        endpoint: str | None = None,
        *,
        mock_mode: bool = True,
        headers: Mapping[str, str] | None = None,
        cache_ttl_seconds: float = 60,
        max_attempts: int = 3,
        min_interval_seconds: float = 0,
        timeout_seconds: float = 15,
    ) -> None:
        if not source.strip():
            raise ValueError("source must not be blank")
        if not mock_mode and not endpoint:
            raise ValueError(f"An endpoint is required for live source {source!r}")
        if (
            cache_ttl_seconds < 0
            or max_attempts < 1
            or min_interval_seconds < 0
            or timeout_seconds <= 0
        ):
            raise ValueError("cache/rate values, retry count, or request timeout are invalid")
        self.source = source
        self.endpoint = endpoint
        self.mock_mode = mock_mode
        self.headers = dict(headers or {})
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_attempts = max_attempts
        self.min_interval_seconds = min_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._cache: dict[str, tuple[float, str, dict[str, Any]]] = {}
        self._rate_lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def fetch(self, params: Mapping[str, Any] | None = None) -> SourceSnapshot:
        request_params = dict(params or {})
        cache_key = hashlib.sha256(
            json.dumps(request_params, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        now = time.monotonic()
        if self.cache_ttl_seconds == 0:
            self._cache.clear()
        else:
            self._cache = {
                key: entry
                for key, entry in self._cache.items()
                if now - entry[0] < self.cache_ttl_seconds
            }
        cached = self._cache.get(cache_key)
        if cached:
            return SourceSnapshot(
                self.source, cached[1], copy.deepcopy(cached[2]), self.mock_mode, cache_hit=True
            )

        payload = (
            _mock_payload(self.source, request_params)
            if self.mock_mode
            else await self._fetch_live(request_params)
        )
        if not isinstance(payload, dict):
            raise SourceAdapterError(f"{self.source} returned a non-object JSON payload")
        fetched_at = datetime.now(timezone.utc).isoformat()
        self._cache[cache_key] = (time.monotonic(), fetched_at, copy.deepcopy(payload))
        return SourceSnapshot(
            self.source, fetched_at, copy.deepcopy(payload), self.mock_mode, cache_hit=False
        )

    async def _fetch_live(self, params: Mapping[str, Any]) -> dict[str, Any]:
        if self.endpoint is None:
            raise SourceAdapterError(f"No endpoint configured for {self.source}")
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        for attempt in range(self.max_attempts):
            await self._wait_for_rate_limit()
            retry_after = 0.0
            try:
                async with aiohttp.ClientSession(
                    timeout=timeout, headers=self.headers
                ) as session:
                    async with session.get(self.endpoint, params=params) as response:
                        if response.status == 429 or response.status >= 500:
                            retry_after = _retry_after_seconds(
                                response.headers.get("Retry-After")
                            )
                            if attempt + 1 == self.max_attempts:
                                raise SourceAdapterError(
                                    f"{self.source} returned retryable HTTP "
                                    f"{response.status} after {self.max_attempts} attempts"
                                )
                            await asyncio.sleep(
                                max(retry_after, min(30.0, 0.5 * (2**attempt)))
                            )
                            continue
                        if response.status < 200 or response.status >= 300:
                            detail = (await response.text())[:300]
                            raise SourceAdapterError(
                                f"{self.source} returned HTTP {response.status}: {detail}"
                            )
                        try:
                            payload = await response.json(content_type=None)
                        except (aiohttp.ContentTypeError, json.JSONDecodeError, ValueError) as exc:
                            raise SourceAdapterError(
                                f"{self.source} returned invalid JSON"
                            ) from exc
                        if not isinstance(payload, dict):
                            raise SourceAdapterError(
                                f"{self.source} returned a non-object JSON payload"
                            )
                        return payload
            except SourceAdapterError:
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                if attempt + 1 == self.max_attempts:
                    raise SourceAdapterError(
                        f"{self.source} request failed after {self.max_attempts} attempts: {exc}"
                    ) from exc
                await asyncio.sleep(min(30.0, 0.5 * (2**attempt)))
        raise SourceAdapterError(f"{self.source} request ended without a response")

    async def _wait_for_rate_limit(self) -> None:
        async with self._rate_lock:
            now = time.monotonic()
            wait_seconds = self.min_interval_seconds - (now - self._last_request_at)
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            self._last_request_at = time.monotonic()


def _retry_after_seconds(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return min(30.0, max(0.0, float(value)))
    except ValueError:
        try:
            target = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return 0.0
        if target.tzinfo is None:
            target = target.replace(tzinfo=timezone.utc)
        return min(30.0, max(0.0, (target - datetime.now(timezone.utc)).total_seconds()))


def _mock_payload(source: str, params: Mapping[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    if source in {
        "open_meteo",
        "open_meteo_ensemble",
        "open_meteo_historical_forecast",
        "open_meteo_archive",
    }:
        hours = range(-720, 73)
        times = [(now.timestamp() + hour * 3600) for hour in hours]
        rain = [
            round(max(0.0, 0.35 + 1.1 * math.sin((hour + 5) / 13)), 2)
            for hour in hours
        ]
        soil = [
            round(min(0.62, max(0.12, 0.28 + 0.00035 * (hour + 720))), 3)
            for hour in hours
        ]
        return {
            "hourly": {
                "time": [
                    datetime.fromtimestamp(value, timezone.utc).isoformat()
                    for value in times
                ],
                "precipitation": rain,
                "soil_moisture_0_to_7cm": soil,
            },
            "latitude": params.get("latitude", 11.35),
            "longitude": params.get("longitude", 76.7),
            "source_label": "MOCK — simulated weather and soil moisture",
            "mock": True,
        }
    if source == "usgs":
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "id": "mock-quake-1",
                    "properties": {
                        "mag": 2.4,
                        "time": int(now.timestamp() * 1000),
                        "place": "MOCK — simulated Nilgiris-region event",
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [76.7, 11.35, 5.0],
                    },
                }
            ],
            "source_label": "MOCK — simulated earthquake fixture",
            "mock": True,
        }
    if source == "gpm_imerg":
        return {
            "records": [
                {
                    "timestamp": (now - timedelta(minutes=30)).isoformat(),
                    "precipitation_mm": 1.2,
                }
            ],
            "source_label": "MOCK — simulated GPM IMERG observation",
            "mock": True,
        }
    if source in {"smap", "era5_land"}:
        return {
            "records": [
                {
                    "timestamp": now.isoformat(),
                    "soil_moisture_fraction": 0.42,
                }
            ],
            "source_label": f"MOCK — simulated {source} soil-moisture observation",
            "mock": True,
        }
    if source == "firms":
        return {
            "records": [
                {
                    "timestamp": now.isoformat(),
                    "latitude": 11.35,
                    "longitude": 76.7,
                    "confidence": 65,
                    "mock_detection": True,
                }
            ],
            "source_label": "MOCK — simulated FIRMS thermal anomaly",
            "mock": True,
        }
    return {
        "source": source,
        "records": [],
        "source_label": f"MOCK — {source} source not queried",
        "mock": True,
    }
