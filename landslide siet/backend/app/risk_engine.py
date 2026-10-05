from typing import Any, Dict, Tuple


def calc_weighted_risk(
    weather: Dict[str, Any],
    terrain: Dict[str, Any],
    satellite: Dict[str, Any],
    historical: Dict[str, Any],
) -> Tuple[int, List[str], Dict[str, float]]:
    """
    Calculate weighted risk score (0-100) from multiple factors.
    Returns: (score, contributing_factors, detailed_breakdown)
    """

    base_score = 30

    # Rainfall component (max 35%)
    rain_24h = float(weather.get("rain_24h_mm", 0))
    rain_72h = float(weather.get("rain_72h_mm", 0))
    rainfall_score = 0
    if rain_24h >= 60:
        rainfall_score = 22
    elif rain_24h >= 25:
        rainfall_score = 10
    elif rain_24h >= 10:
        rainfall_score = 5

    if rain_72h >= 150:
        rainfall_score = min(35, rainfall_score + 15)
    elif rain_72h >= 75:
        rainfall_score = min(35, rainfall_score + 8)

    # Soil moisture component (max 25%)
    soil_moisture = float(weather.get("soil_moisture", 0))
    moisture_score = 0
    if soil_moisture >= 75:
        moisture_score = 25
    elif soil_moisture >= 65:
        moisture_score = 15
    elif soil_moisture >= 50:
        moisture_score = 8

    # Slope component (max 20%)
    slope = float(terrain.get("slope_deg", 0))
    slope_score = 0
    if slope >= 30:
        slope_score = 20
    elif slope >= 25:
        slope_score = 16
    elif slope >= 15:
        slope_score = 8

    # Vegetation/NDVI component (max 15%)
    ndvi = float(satellite.get("ndvi", 0.5))
    veg_score = 0
    if ndvi < 0.35:
        veg_score = 15
    elif ndvi < 0.45:
        veg_score = 10
    elif ndvi < 0.60:
        veg_score = 5

    # Historical component (max 18%)
    hist_incidents = float(historical.get("historical_landslides_nearby", 0))
    hist_score = 0
    if hist_incidents >= 4:
        hist_score = 18
    elif hist_incidents >= 2:
        hist_score = 8
    elif hist_incidents >= 1:
        hist_score = 4

    # Calculate total
    total_score = int(
        min(100, base_score + rainfall_score + moisture_score + slope_score + veg_score + hist_score)
    )

    # Contributing factors
    factors = []
    if rain_24h >= 25:
        factors.append("Heavy rainfall")
    if soil_moisture >= 65:
        factors.append("High soil moisture")
    if slope >= 25:
        factors.append("High slope")
    if ndvi < 0.45:
        factors.append("Low vegetation stability")
    if hist_incidents >= 1:
        factors.append("Historical landslides nearby")

    breakdown = {
        "base": base_score,
        "rainfall": rainfall_score,
        "moisture": moisture_score,
        "slope": slope_score,
        "vegetation": veg_score,
        "historical": hist_score,
    }

    return total_score, factors, breakdown
