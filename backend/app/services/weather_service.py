import httpx
from typing import Optional

DISTRICT_COORDINATES = {
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Nashik": {"lat": 20.0059, "lon": 73.7897},
    "Aurangabad": {"lat": 19.8762, "lon": 75.3433},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    "Solapur": {"lat": 17.6868, "lon": 75.9064},
    "Kolhapur": {"lat": 16.7050, "lon": 74.2433},
    "Satara": {"lat": 17.6805, "lon": 74.0183},
    "Sangli": {"lat": 16.8524, "lon": 74.5815},
    "Ahmednagar": {"lat": 19.0948, "lon": 74.7480},
    "Latur": {"lat": 18.4088, "lon": 76.5604},
}

async def get_weather_forecast(district: str) -> dict:
    coords = DISTRICT_COORDINATES.get(district)
    if not coords:
        return {
            "district": district,
            "status": "coordinates not found",
            "forecast": []
        }

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={coords['lat']}"
        f"&longitude={coords['lon']}"
        f"&daily=temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,windspeed_10m_max"
        f"&timezone=Asia%2FKolkata"
        f"&forecast_days=7"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        data = response.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rainfall = daily.get("precipitation_sum", [])
    windspeed = daily.get("windspeed_10m_max", [])

    forecast = []
    for i in range(len(dates)):
        forecast.append({
            "date": dates[i],
            "max_temp": max_temps[i],
            "min_temp": min_temps[i],
            "rainfall_mm": rainfall[i],
            "windspeed_kmh": windspeed[i],
            "alert": get_weather_alert(
                rainfall[i],
                max_temps[i],
                windspeed[i]
            )
        })

    return {
        "district": district,
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "forecast": forecast
    }

def get_weather_alert(rainfall: float, max_temp: float,
                      windspeed: float) -> Optional[str]:
    if rainfall and rainfall > 50:
        return "Heavy rainfall expected — protect crops from waterlogging"
    if rainfall and rainfall > 20:
        return "Moderate rainfall expected — good for irrigation-dependent crops"
    if max_temp and max_temp > 42:
        return "Extreme heat alert — increase irrigation frequency"
    if max_temp and max_temp > 38:
        return "High temperature — monitor crop stress"
    if windspeed and windspeed > 50:
        return "Strong winds expected — secure tall crops"
    return None