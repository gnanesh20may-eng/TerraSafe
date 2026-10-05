"""Provider-specific request setup and all-source adapter construction."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from backend.app.ingest.base import AsyncJSONIngestor, SourceAdapterError

SOURCE_NAMES = (
    "open_meteo",
    "open_meteo_ensemble",
    "open_meteo_historical_forecast",
    "open_meteo_archive",
    "gpm_imerg",
    "smap",
    "era5_land",
    "usgs",
    "firms",
    "imd_mosdac",
)


class OpenMeteoIngestor(AsyncJSONIngestor):
    """Open-Meteo forecast endpoint; mock mode remains the default."""

    def __init__(
        self,
        *,
        mock_mode: bool = True,
        endpoint: str = "https://api.open-meteo.com/v1/forecast",
        source: str = "open_meteo",
        **options: Any,
    ) -> None:
        super().__init__(
            source,
            endpoint,
            mock_mode=mock_mode,
            **options,
        )

    async def fetch(self, params: Mapping[str, Any] | None = None):
        query = {
            "latitude": 11.35,
            "longitude": 76.7,
            "hourly": "precipitation,soil_moisture_0_to_7cm",
            "timezone": "UTC",
        }
        query.update(params or {})
        if not -90 <= float(query["latitude"]) <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= float(query["longitude"]) <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return await super().fetch(query)


class OpenMeteoEnsembleIngestor(OpenMeteoIngestor):
    """Open-Meteo ensemble member forecasts."""

    def __init__(self, *, mock_mode: bool = True, **options: Any) -> None:
        super().__init__(
            mock_mode=mock_mode,
            endpoint="https://ensemble-api.open-meteo.com/v1/ensemble",
            source="open_meteo_ensemble",
            **options,
        )


class OpenMeteoHistoricalForecastIngestor(OpenMeteoIngestor):
    """Archive of previously issued weather forecasts."""

    def __init__(self, *, mock_mode: bool = True, **options: Any) -> None:
        super().__init__(
            mock_mode=mock_mode,
            endpoint="https://historical-forecast-api.open-meteo.com/v1/forecast",
            source="open_meteo_historical_forecast",
            **options,
        )

    async def fetch(self, params: Mapping[str, Any] | None = None):
        if not self.mock_mode:
            _validate_date_range(params)
        return await super().fetch(params)


class OpenMeteoHistoricalWeatherIngestor(OpenMeteoIngestor):
    """Historical observed/reanalysis weather archive."""

    def __init__(self, *, mock_mode: bool = True, **options: Any) -> None:
        super().__init__(
            mock_mode=mock_mode,
            endpoint="https://archive-api.open-meteo.com/v1/archive",
            source="open_meteo_archive",
            **options,
        )

    async def fetch(self, params: Mapping[str, Any] | None = None):
        if not self.mock_mode:
            _validate_date_range(params)
        return await super().fetch(params)


class USGSEarthquakeIngestor(AsyncJSONIngestor):
    """USGS FDSN GeoJSON earthquake query endpoint."""

    def __init__(self, *, mock_mode: bool = True, **options: Any) -> None:
        super().__init__(
            "usgs",
            "https://earthquake.usgs.gov/fdsnws/event/1/query",
            mock_mode=mock_mode,
            **options,
        )

    async def fetch(self, params: Mapping[str, Any] | None = None):
        current = datetime.now(timezone.utc)
        query = {
            "format": "geojson",
            "starttime": (current - timedelta(days=7)).isoformat(),
            "endtime": current.isoformat(),
        }
        query.update(params or {})
        if query.get("format") != "geojson":
            raise ValueError("USGS adapter requires format=geojson")
        return await super().fetch(query)


def _validate_date_range(params: Mapping[str, Any] | None) -> None:
    if not params or not params.get("start_date") or not params.get("end_date"):
        raise ValueError("historical requests require start_date and end_date")
    try:
        from datetime import date

        start = date.fromisoformat(str(params["start_date"]))
        end = date.fromisoformat(str(params["end_date"]))
    except ValueError as exc:
        raise ValueError("historical dates must use YYYY-MM-DD format") from exc
    if start > end:
        raise ValueError("start_date must not be after end_date")


def build_ingestors(
    *,
    mock_mode: bool = True,
    endpoints: Mapping[str, str] | None = None,
    headers: Mapping[str, Mapping[str, str]] | None = None,
) -> dict[str, AsyncJSONIngestor]:
    """Create adapters for all P2 sources without requiring credentials in mock mode.

    Live NASA/IMD integrations require an operator-configured endpoint and
    headers because those services have product-specific APIs and credentials.
    """
    configured_endpoints = dict(endpoints or {})
    configured_headers = dict(headers or {})
    open_meteo_classes = {
        "open_meteo": OpenMeteoIngestor,
        "open_meteo_ensemble": OpenMeteoEnsembleIngestor,
        "open_meteo_historical_forecast": OpenMeteoHistoricalForecastIngestor,
        "open_meteo_archive": OpenMeteoHistoricalWeatherIngestor,
    }
    if mock_mode:
        return {
            name: open_meteo_classes[name](mock_mode=True)
            if name in open_meteo_classes
            else AsyncJSONIngestor(name, mock_mode=True)
            for name in SOURCE_NAMES
        }

    missing = [
        name
        for name in SOURCE_NAMES
        if name not in {*open_meteo_classes, "usgs"} and not configured_endpoints.get(name)
    ]
    if missing:
        raise SourceAdapterError(
            "Live adapters need configured endpoints for: " + ", ".join(missing)
        )
    return {
        **{
            name: adapter_class(
                mock_mode=False,
                headers=configured_headers.get(name),
            )
            for name, adapter_class in open_meteo_classes.items()
        },
        "usgs": USGSEarthquakeIngestor(
            mock_mode=False, headers=configured_headers.get("usgs")
        ),
        **{
            name: AsyncJSONIngestor(
                name,
                configured_endpoints[name],
                mock_mode=False,
                headers=configured_headers.get(name),
            )
            for name in SOURCE_NAMES
            if name not in {*open_meteo_classes, "usgs"}
        },
    }
