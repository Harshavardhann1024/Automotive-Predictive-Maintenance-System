"""
Agent Schemas — Pydantic models for the agent pipeline API.
============================================================
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class AgentPredictRequest(BaseModel):
    """Input for the /agents/predict-and-act endpoint."""
    engine_temp: float = Field(..., description="Engine temperature (°C)", ge=0, le=300)
    oil_pressure: float = Field(..., description="Oil pressure (psi)", ge=0, le=100)
    rpm: float = Field(..., description="Engine RPM", ge=0, le=10000)
    vibration: float = Field(..., description="Vibration level (g)", ge=0, le=5)
    battery_voltage: float = Field(..., description="Battery voltage (V)", ge=0, le=20)
    mileage: float = Field(..., description="Vehicle mileage (km)", ge=0)
    vehicle_id: Optional[UUID] = Field(None, description="Optional vehicle ID for service scheduling")


class ServiceInfoResponse(BaseModel):
    """Service scheduling details (when a service is scheduled)."""
    service_request_id: str
    scheduled_time: str
    status: str


class AgentPredictResponse(BaseModel):
    """Unified response from the predict-and-act pipeline."""
    # Prediction results
    probability: float = Field(..., description="Failure probability (0-1)")
    risk_level: str = Field(..., description="Risk classification: LOW / MEDIUM / HIGH")
    prediction: int = Field(..., description="Binary prediction (0 = no failure, 1 = failure)")
    sensor_flags: List[str] = Field(default=[], description="Triggered domain rules")
    threshold_used: float = Field(..., description="Model threshold used")

    # Action results
    action_taken: str = Field(..., description="Action taken: LOG_ONLY / NOTIFY / SERVICE_SCHEDULED")
    service_scheduled: bool = Field(..., description="Whether a service was scheduled")
    service_info: Optional[ServiceInfoResponse] = Field(None, description="Service details if scheduled")
    notification_sent: bool = Field(..., description="Whether a notification was dispatched")
    reason: str = Field(..., description="Human-readable explanation of the decision")

    class Config:
        from_attributes = True
