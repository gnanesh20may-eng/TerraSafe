DEMO_LOCATIONS = {
    "Ooty": {
        "lat": 11.4064, "lon": 76.6932, "country": "India", "state": "Tamil Nadu", "region": "Nilgiris",
        "elevation_m": 2240, "slope_deg": 31.2, "soil_moisture": 71, "temperature_c": 18.5, "humidity": 83,
        "wind_kph": 13.2, "rain_1h_mm": 8.8, "rain_3h_mm": 19.1, "rain_6h_mm": 29.7,
        "rain_24h_mm": 64.4, "rain_72h_mm": 121.0, "ndvi": 0.46, "vegetation_cover": "moderate",
        "historical_landslides_nearby": 4, "roads_proximity_km": 0.9, "settlements_proximity_km": 0.7,
        "reference_hazard": "elevated terrain instability observed", "sentinel_cloud_cover_pct": 18
    },
    "Wayanad": {
        "lat": 11.6854, "lon": 76.1321, "country": "India", "state": "Kerala", "region": "Western Ghats",
        "elevation_m": 700, "slope_deg": 26.4, "soil_moisture": 76, "temperature_c": 22.1, "humidity": 88,
        "wind_kph": 15.6, "rain_1h_mm": 12.1, "rain_3h_mm": 22.5, "rain_6h_mm": 35.0,
        "rain_24h_mm": 89.6, "rain_72h_mm": 180.2, "ndvi": 0.52, "vegetation_cover": "moderate",
        "historical_landslides_nearby": 7, "roads_proximity_km": 1.2, "settlements_proximity_km": 1.5,
        "reference_hazard": "high rainfall-triggered instability", "sentinel_cloud_cover_pct": 22
    },
    "Kodaikanal": {
        "lat": 10.2381, "lon": 77.4892, "country": "India", "state": "Tamil Nadu", "region": "Palani Hills",
        "elevation_m": 2133, "slope_deg": 28.1, "soil_moisture": 68, "temperature_c": 17.0, "humidity": 81,
        "wind_kph": 11.7, "rain_1h_mm": 7.3, "rain_3h_mm": 18.9, "rain_6h_mm": 24.4,
        "rain_24h_mm": 52.0, "rain_72h_mm": 116.6, "ndvi": 0.55, "vegetation_cover": "good",
        "historical_landslides_nearby": 3, "roads_proximity_km": 1.0, "settlements_proximity_km": 0.8,
        "reference_hazard": "slope-driven susceptibility", "sentinel_cloud_cover_pct": 16
    },
    "Darjeeling": {
        "lat": 27.0410, "lon": 88.2663, "country": "India", "state": "West Bengal", "region": "Eastern Himalaya",
        "elevation_m": 2072, "slope_deg": 34.4, "soil_moisture": 79, "temperature_c": 14.8, "humidity": 90,
        "wind_kph": 19.2, "rain_1h_mm": 13.6, "rain_3h_mm": 29.2, "rain_6h_mm": 44.4,
        "rain_24h_mm": 98.1, "rain_72h_mm": 190.5, "ndvi": 0.44, "vegetation_cover": "variable",
        "historical_landslides_nearby": 8, "roads_proximity_km": 0.6, "settlements_proximity_km": 0.7,
        "reference_hazard": "steep slope and heavy rainfall", "sentinel_cloud_cover_pct": 29
    },
    "Sikkim": {
        "lat": 27.3389, "lon": 88.6065, "country": "India", "state": "Sikkim", "region": "Himalayan belt",
        "elevation_m": 1800, "slope_deg": 32.6, "soil_moisture": 73, "temperature_c": 15.2, "humidity": 87,
        "wind_kph": 16.4, "rain_1h_mm": 10.3, "rain_3h_mm": 23.8, "rain_6h_mm": 38.6,
        "rain_24h_mm": 80.4, "rain_72h_mm": 167.6, "ndvi": 0.47, "vegetation_cover": "moderate",
        "historical_landslides_nearby": 6, "roads_proximity_km": 0.8, "settlements_proximity_km": 0.9,
        "reference_hazard": "high rainfall and steep terrain", "sentinel_cloud_cover_pct": 21
    },
}


def get_demo_location(lat: float, lon: float):
    for name, data in DEMO_LOCATIONS.items():
        if abs(lat - data["lat"]) < 0.5 and abs(lon - data["lon"]) < 0.5:
            return name, data
    nearest = min(DEMO_LOCATIONS.items(), key=lambda item: ((lat - item[1]["lat"]) ** 2 + (lon - item[1]["lon"]) ** 2) ** 0.5)
    return nearest[0], nearest[1]
