from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.cascade_engine import calculate_cascade
from app.services.weather_service import fetch_live_weather

router = APIRouter()


class HazardInput(BaseModel):
    rainfall_mm: float = Field(ge=0, le=1000)
    wind_speed_kmh: float = Field(ge=0, le=500)
    lightning_probability: float = Field(ge=0, le=1)
    thunderstorm_intensity: float = Field(ge=0, le=1)


INFRASTRUCTURE = [
    {"type": "power_grid", "name": "Central Power Station"},
    {"type": "road", "name": "Main Highway"},
    {"type": "hospital", "name": "City General Hospital"},
    {"type": "traffic", "name": "Central Traffic Network"},
]


SCENARIOS = {
    "storm": {
        "rainfall_mm": 120,
        "wind_speed_kmh": 75,
        "lightning_probability": 0.8,
        "thunderstorm_intensity": 0.9,
    },
    "rain": {
        "rainfall_mm": 100,
        "wind_speed_kmh": 35,
        "lightning_probability": 0.2,
        "thunderstorm_intensity": 0.3,
    },
    "normal": {
        "rainfall_mm": 10,
        "wind_speed_kmh": 15,
        "lightning_probability": 0.05,
        "thunderstorm_intensity": 0.05,
    },
}


@router.get("/status")
def status():
    return {"system": "CityPulse X", "status": "operational"}


def build_result(weather, scenario):
    prediction = calculate_cascade(weather, INFRASTRUCTURE)
    return {
        "city": "Demo City",
        "scenario": scenario,
        "weather": weather,
        "prediction": prediction,
    }


@router.get("/cascade")
def run_cascade(scenario: str = "storm"):
    selected = scenario.lower()
    if selected not in SCENARIOS:
        selected = "storm"
    return build_result(SCENARIOS[selected], selected)


@router.post("/analyze")
def analyze_custom(hazard: HazardInput):
    weather = {
        "rainfall_mm": hazard.rainfall_mm,
        "wind_speed_kmh": hazard.wind_speed_kmh,
        "lightning_probability": hazard.lightning_probability,
        "thunderstorm_intensity": hazard.thunderstorm_intensity,
    }
    return build_result(weather, "custom")


@router.get("/live-weather")
def live_weather(city: str):
    try:
        weather = fetch_live_weather(city)
        result = build_result(weather, "live")
        result["city"] = weather["city"]
        result["weather_source"] = weather["source"]
        result["weather_data_type"] = weather["data_type"]
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve live weather. Check your internet connection and try again.",
        ) from exc
