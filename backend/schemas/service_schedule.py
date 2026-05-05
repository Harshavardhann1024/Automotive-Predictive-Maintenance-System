"""
Service Schedule schemas — Pydantic models for request/response.
================================================================
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ServiceScheduleBase(BaseModel):
    """Base fields shared across request/response."""
    vehicle_id: Optional[UUID] = None
    prediction_id: Optional[UUID] = None
    service_type: str = Field(..., description="inspection | repair | urgent")
    priority: str = Field(..., description="low | medium | high")
    status: str = Field("pending", description="pending | scheduled | in_progress | completed | cancelled")
    scheduled_date: datetime
    failure_probability: Optional[float] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None
    technician: Optional[str] = None


class ServiceScheduleResponse(BaseModel):
    """Full service schedule record returned from API."""
    id: UUID
    vehicle_id: Optional[UUID] = None
    prediction_id: Optional[UUID] = None
    service_type: str
    priority: str
    status: str
    scheduled_date: datetime
    failure_probability: Optional[float] = None
    risk_level: Optional[str] = None
    notes: Optional[str] = None
    technician: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ServiceScheduleUpdate(BaseModel):
    """Partial update for a service schedule (PATCH)."""
    status: Optional[str] = Field(None, description="pending | scheduled | in_progress | completed | cancelled")
    scheduled_date: Optional[datetime] = None
    technician: Optional[str] = None
    notes: Optional[str] = None


class ServiceScheduleStats(BaseModel):
    """Dashboard summary statistics for service schedules."""
    total_schedules: int = 0
    pending_count: int = 0
    scheduled_count: int = 0
    in_progress_count: int = 0
    completed_count: int = 0
    cancelled_count: int = 0
    high_priority_count: int = 0
    medium_priority_count: int = 0
    low_priority_count: int = 0
    upcoming_24h: int = 0
    overdue_count: int = 0
    urgent_services: int = 0
    inspection_services: int = 0
    repair_services: int = 0
