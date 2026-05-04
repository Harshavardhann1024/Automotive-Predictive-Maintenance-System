"""
Prediction schemas — Pydantic models for request/response.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class PredictionRequest(BaseModel):
    """Input sensor data for a failure prediction."""
    engine_temp: float = Field(..., description="Engine temperature (°C)", ge=0, le=300)
    oil_pressure: float = Field(..., description="Oil pressure (psi)", ge=0, le=100)
    rpm: float = Field(..., description="Engine RPM", ge=0, le=10000)
    vibration: float = Field(..., description="Vibration level (g)", ge=0, le=5)
    battery_voltage: float = Field(..., description="Battery voltage (V)", ge=0, le=20)
    mileage: float = Field(..., description="Vehicle mileage (km)", ge=0)
    vehicle_id: Optional[UUID] = Field(None, description="Optional vehicle ID to link prediction")


class PredictionResponse(BaseModel):
    """ML prediction result."""
    failure_probability: float
    prediction: int
    risk_level: str
    sensor_flags: List[str] = []
    threshold_used: float

    class Config:
        from_attributes = True


class PredictionHistoryResponse(BaseModel):
    """Stored prediction record from database."""
    id: UUID
    vehicle_id: Optional[UUID]
    engine_temp: float
    oil_pressure: float
    rpm: float
    vibration: float
    battery_voltage: float
    mileage: float
    failure_probability: float
    prediction: int
    risk_level: str
    threshold_used: float
    created_at: datetime

    class Config:
        from_attributes = True


class ModelInfoResponse(BaseModel):
    """Information about the loaded ML model."""
    model_version: str
    threshold: float
    domain_rules_active: bool
    training_metrics: dict
    feature_order: List[str]


class PredictionStats(BaseModel):
    """Aggregated prediction statistics for dashboard."""
    total_predictions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    avg_failure_probability: float
    recent_failure_rate: float
