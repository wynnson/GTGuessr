import json
from urllib.request import Request, urlopen
from django.conf import settings
from django.shortcuts import render

GT_LAT = 33.7756
GT_LON = -84.3963


def fetch_weather():
    base_headers = {"User-Agent": "GTGuessr (gtguessr)"}

    try:
        points_req = Request(
            f"https://api.weather.gov/points/{GT_LAT},{GT_LON}",
            headers=base_headers,
        )
        with urlopen(points_req, timeout=4) as resp:
            points_data = json.load(resp)
        forecast_url = points_data.get("properties", {}).get("forecast")
        if not forecast_url:
            return None

        forecast_req = Request(forecast_url, headers=base_headers)
        with urlopen(forecast_req, timeout=4) as resp:
            forecast_data = json.load(resp)

        periods = forecast_data.get("properties", {}).get("periods", [])
        if not periods:
            return None

        current = periods[0]
        return {
            "temperature": current.get("temperature"),
            "temperature_unit": current.get("temperatureUnit"),
            "short_forecast": current.get("shortForecast"),
            "wind_speed": current.get("windSpeed"),
            "wind_direction": current.get("windDirection"),
            "detailed_forecast": current.get("detailedForecast"),
            "name": current.get("name"),
        }
    except Exception:
        return None

def index(request):
    return render(request, "home/index.html", {
        "mapbox_token": settings.MAPBOX_TOKEN,
        "weather": fetch_weather(),
    })
