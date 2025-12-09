import json
from urllib.request import Request, urlopen
from django.conf import settings
from django.shortcuts import render

GT_LAT = 33.7756
GT_LON = -84.3963


import json
from urllib.request import Request, urlopen

GT_LAT = 33.7756
GT_LON = -84.3963

def fetch_weather():
    base_headers = {"User-Agent": "GTGuessr (gtguessr)"}

    try:
        points_url = f"https://api.weather.gov/points/{GT_LAT},{GT_LON}"
        with urlopen(Request(points_url, headers=base_headers), timeout=4) as resp:
            points_data = json.load(resp)

        forecast_url = points_data["properties"]["forecast"]
        stations_url = points_data["properties"]["observationStations"]

        with urlopen(Request(stations_url, headers=base_headers), timeout=4) as resp:
            stations_data = json.load(resp)

        station = stations_data["features"][0]["properties"]["stationIdentifier"]

        obs_url = f"https://api.weather.gov/stations/{station}/observations/latest"
        with urlopen(Request(obs_url, headers=base_headers), timeout=4) as resp:
            obs_data = json.load(resp)

        obs = obs_data.get("properties", {})

        temp_c = obs.get("temperature", {}).get("value")
        wind_ms = obs.get("windSpeed", {}).get("value")
        wind_dir = obs.get("windDirection", {}).get("value")
        short_desc = obs.get("textDescription")

        if temp_c is None:
            return None

        def degrees_to_cardinal(deg):
            if deg is None:
                return None
            dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            ix = round(deg / 45) % 8
            return dirs[ix]

        wind_cardinal = degrees_to_cardinal(wind_dir)

        with urlopen(Request(forecast_url, headers=base_headers), timeout=4) as resp:
            forecast_data = json.load(resp)

        periods = forecast_data.get("properties", {}).get("periods", [])
        detailed_forecast = periods[0].get("detailedForecast") if periods else None

        return {
            "temperature": round((temp_c * 9/5) + 32, 1),
            "temperature_unit": "F",
            "short_forecast": short_desc,
            "wind_speed": wind_ms,
            "wind_direction": wind_cardinal,
            "detailed_forecast": detailed_forecast,
        }

    except Exception:
        return None


def index(request):
    return render(request, "home/index.html", {
        "mapbox_token": settings.MAPBOX_TOKEN,
        "weather": fetch_weather(),
    })
