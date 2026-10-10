import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_json(url, params):
    full_url = url + "?" + urlencode(params)
    request = Request(
        full_url,
        headers={"User-Agent": "CityPulse-X/1.0"}
    )

    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_live_weather(city: str) -> dict:
    city = city.strip()

    if not city:
        raise ValueError("Please enter a city name.")

    locations = fetch_json(
        GEOCODING_URL,
        {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )

    results = locations.get("results", [])

    if not results:
        raise ValueError(
            f"Could not find the city '{city}'. Check the spelling."
        )

    location = results[0]

    weather = fetch_json(
        FORECAST_URL,
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "rain,"
                "wind_speed_10m,"
                "wind_gusts_10m,"
                "weather_code"
            ),
            "hourly": "precipitation_probability",
            "forecast_hours": 1,
            "timezone": "auto",
        },
    )

    current = weather.get("current", {})
    hourly = weather.get("hourly", {})

    probabilities = hourly.get("precipitation_probability", [])
    rain_probability = (
        float(probabilities[0])
        if probabilities and probabilities[0] is not None
        else 0.0
    )

    weather_code = current.get("weather_code")
    is_thunderstorm = weather_code in (95, 96, 99)

    return {
        "city": location.get("name", city),
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "time": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "rainfall_mm": float(current.get("precipitation") or 0),
        "wind_speed_kmh": float(current.get("wind_speed_10m") or 0),
        "wind_gusts_kmh": float(current.get("wind_gusts_10m") or 0),
        "lightning_probability": 0.7 if is_thunderstorm else 0.0,
        "thunderstorm_intensity": 0.7 if is_thunderstorm else 0.0,
        "precipitation_probability_percent": rain_probability,
        "weather_code": weather_code,
        "source": "Open-Meteo",
        "data_type": "Weather model estimate and forecast",
    }
