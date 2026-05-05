"""
Prediction schemas — Pydantic models for request/response.
Includes SHAP explainability response models.
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


# ─── SHAP Explanation Models ──────────────────────────────

class FeatureExplanation(BaseModel):
    """Single feature's SHAP contribution to the prediction."""
    feature: str = Field(..., description="Feature name (e.g. engine_temp)")
    impact: float = Field(..., description="SHAP value — positive increases failure risk, negative decreases it")
    value: float = Field(..., description="Actual sensor value used for this feature")


class SHAPExplanation(BaseModel):
    """Complete SHAP explanation payload for a prediction."""
    explanations: List[FeatureExplanation] = Field(
        default_factory=list,
        description="Feature contributions sorted by absolute impact (descending)",
    )
    natural_explanation: str = Field(
        "",
        description="Human-readable summary of why this prediction was made",
    )
    shap_base_value: Optional[float] = Field(
        None,
        description="SHAP expected value (baseline prediction before feature contributions)",
    )
    suppressed_by_rules: bool = Field(
        False,
        description="True if domain safety rules suppressed the ML prediction",
    )
    suppression_note: Optional[str] = Field(
        None,
        description="Explanation of why the prediction was suppressed",
    )


class PredictionResponse(BaseModel):
    """ML prediction result — optionally includes SHAP explanation."""
    failure_probability: float
    prediction: int
    risk_level: str
    sensor_flags: List[str] = []
    threshold_used: float

    # SHAP fields (populated only when ?explain=true)
    explanations: Optional[List[FeatureExplanation]] = None
    natural_explanation: Optional[str] = None
    shap_base_value: Optional[float] = None
    suppressed_by_rules: Optional[bool] = None
    suppression_note: Optional[str] = None

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
