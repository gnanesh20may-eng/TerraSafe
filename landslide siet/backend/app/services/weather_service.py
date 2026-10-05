from backend.app.config import DEMO_MODE, OPENMETEO_BASE_URL
from backend.app.demo_data import get_demo_location
from backend.app.services.base import fetch_json


def get_weather_data(lat: float, lon: float):
    if DEMO_MODE:
        _, demo = get_demo_location(lat, lon)
        return {
            "status": "cached",
            "temperature_c": demo.get("temperature_c", 20),
            "humidity": demo.get("humidity", 75),
            "wind_kph": demo.get("wind_kph", 12),
            "rain_1h_mm": demo.get("rain_1h_mm", 5),
            "rain_3h_mm": demo.get("rain_3h_mm", 15),
            "rain_6h_mm": demo.get("rain_6h_mm", 25),
            "rain_24h_mm": demo.get("rain_24h_mm", 60),
            "rain_72h_mm": demo.get("rain_72h_mm", 120),
            "soil_moisture": demo.get("soil_moisture", 70),
            "forecast": [{"time": "2026-10-05T12:00", "rain_mm": demo.get("rain_1h_mm", 5)}],
            "source": "DEMO_DATA",
        }

    try:
        data = fetch_json(f"{OPENMETEO_BASE_URL}/forecast", params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,soil_moisture_0_7cm,wind_speed_10m",
            "timezone": "auto",
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        })
        current = data.get("current", {})
        return {
            "status": "connected",
            "temperature_c": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_kph": current.get("wind_speed_10m"),
            "rain_1h_mm": 0,
            "rain_3h_mm": 0,
            "rain_6h_mm": 0,
            "rain_24h_mm": 0,
            "rain_72h_mm": 0,
            "soil_moisture": 0,
            "forecast": data.get("hourly", {}).get("precipitation", [])[:10],
            "source": "open-meteo",
        }
    except Exception:
        return {
            "status": "temporarily unavailable",
            "temperature_c": None,
            "humidity": None,
            "wind_kph": None,
            "rain_1h_mm": None,
            "rain_3h_mm": None,
            "rain_6h_mm": None,
            "rain_24h_mm": None,
            "rain_72h_mm": None,
            "soil_moisture": None,
            "forecast": [],
            "source": "fallback",
        }
