# Demo locations for DEMO_MODE
# Used when real APIs are unavailable or in development

DEMO_LOCATIONS = {
    "Ooty, Nilgiris": {
        "lat": 11.4064,
        "lon": 76.6932,
        "region": "Nilgiris",
        "state": "Tamil Nadu",
        "country": "India",
        "elevation_m": 2240,
        "slope_deg": 31,
        "roads_proximity_km": 1.2,
        "settlements_proximity_km": 0.8,
        "temperature_c": 18.5,
        "humidity": 83,
        "wind_kph": 12,
        "rain_1h_mm": 5.2,
        "rain_3h_mm": 14.8,
        "rain_6h_mm": 28.4,
        "rain_24h_mm": 64.4,
        "rain_72h_mm": 128.8,
        "soil_moisture": 78,
        "ndvi": 0.46,
        "vegetation_cover": "moderate",
        "sentinel_cloud_cover_pct": 35,
        "reference_hazard": "high susceptibility zone",
        "historical_landslides_nearby": 4,
    },
    "Wayanad, Kerala": {
        "lat": 11.6854,
        "lon": 76.1321,
        "region": "Wayanad",
        "state": "Kerala",
        "country": "India",
        "elevation_m": 800,
        "slope_deg": 32,
        "roads_proximity_km": 0.5,
        "settlements_proximity_km": 1.0,
        "temperature_c": 22.3,
        "humidity": 88,
        "wind_kph": 8,
        "rain_1h_mm": 8.5,
        "rain_3h_mm": 18.2,
        "rain_6h_mm": 35.6,
        "rain_24h_mm": 142.0,
        "rain_72h_mm": 215.0,
        "soil_moisture": 82,
        "ndvi": 0.42,
        "vegetation_cover": "low",
        "sentinel_cloud_cover_pct": 75,
        "reference_hazard": "very high susceptibility zone",
        "historical_landslides_nearby": 7,
    },
    "Kodaikanal, Tamil Nadu": {
        "lat": 10.2381,
        "lon": 77.4892,
        "region": "Dindigul",
        "state": "Tamil Nadu",
        "country": "India",
        "elevation_m": 2145,
        "slope_deg": 20,
        "roads_proximity_km": 2.0,
        "settlements_proximity_km": 1.5,
        "temperature_c": 16.2,
        "humidity": 72,
        "wind_kph": 10,
        "rain_1h_mm": 2.1,
        "rain_3h_mm": 5.4,
        "rain_6h_mm": 12.8,
        "rain_24h_mm": 48.0,
        "rain_72h_mm": 72.0,
        "soil_moisture": 54,
        "ndvi": 0.58,
        "vegetation_cover": "dense",
        "sentinel_cloud_cover_pct": 15,
        "reference_hazard": "low to moderate susceptibility",
        "historical_landslides_nearby": 2,
    },
    "Darjeeling, West Bengal": {
        "lat": 27.0410,
        "lon": 88.2663,
        "region": "Darjeeling",
        "state": "West Bengal",
        "country": "India",
        "elevation_m": 2205,
        "slope_deg": 34,
        "roads_proximity_km": 0.3,
        "settlements_proximity_km": 0.5,
        "temperature_c": 14.8,
        "humidity": 91,
        "wind_kph": 15,
        "rain_1h_mm": 9.2,
        "rain_3h_mm": 22.5,
        "rain_6h_mm": 42.0,
        "rain_24h_mm": 160.0,
        "rain_72h_mm": 240.0,
        "soil_moisture": 85,
        "ndvi": 0.38,
        "vegetation_cover": "low",
        "sentinel_cloud_cover_pct": 95,
        "reference_hazard": "very high susceptibility zone",
        "historical_landslides_nearby": 8,
    },
    "Sikkim": {
        "lat": 27.5330,
        "lon": 88.5122,
        "region": "Sikkim",
        "state": "Sikkim",
        "country": "India",
        "elevation_m": 1600,
        "slope_deg": 38,
        "roads_proximity_km": 1.8,
        "settlements_proximity_km": 2.0,
        "temperature_c": 15.5,
        "humidity": 89,
        "wind_kph": 16,
        "rain_1h_mm": 6.8,
        "rain_3h_mm": 17.2,
        "rain_6h_mm": 38.5,
        "rain_24h_mm": 135.0,
        "rain_72h_mm": 198.0,
        "soil_moisture": 80,
        "ndvi": 0.40,
        "vegetation_cover": "moderate",
        "sentinel_cloud_cover_pct": 88,
        "reference_hazard": "high susceptibility zone",
        "historical_landslides_nearby": 6,
    },
}


def get_demo_location(lat: float, lon: float) -> tuple:
    """
    Find nearest demo location to given coordinates.
    Returns: (location_name, demo_data_dict)
    """
    if not DEMO_LOCATIONS:
        return "Unknown", {}

    min_distance = float("inf")
    nearest_location = None
    nearest_data = None

    for name, data in DEMO_LOCATIONS.items():
        distance = ((data["lat"] - lat) ** 2 + (data["lon"] - lon) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            nearest_location = name
            nearest_data = data

    return nearest_location or "Unknown", nearest_data or {}
