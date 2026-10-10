from pydantic import BaseModel, Field
from typing import List, Optional


class WeatherState(BaseModel):
    rainfall_mm: float = Field(0, ge=0)
    wind_speed_kmh: float = Field(0, ge=0)
    lightning_probability: float = Field(0, ge=0, le=1)
    thunderstorm_intensity: float = Field(0, ge=0, le=1)
    temperature_c: float = 0


class InfrastructureNode(BaseModel):
    node_id: str
    name: str
    node_type: str
    capacity: float = Field(100, ge=0, le=100)
    current_load: float = Field(0, ge=0, le=100)
    criticality: float = Field(0.5, ge=0, le=1)
    latitude: float
    longitude: float


class CityState(BaseModel):
    city: str
    weather: WeatherState
    infrastructure: List[InfrastructureNode] = []
    traffic_level: float = Field(0, ge=0, le=100)
    hospital_stress: float = Field(0, ge=0, le=100)
    telecom_stress: float = Field(0, ge=0, le=100)
    population_exposure: float = Field(0, ge=0, le=100)


class RiskResponse(BaseModel):
    overall_risk: float
    risk_level: str
    primary_hazard: str
    expected_cascade: List[str]
    confidence: float
    explanation: str
