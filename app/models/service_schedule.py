"""
ServiceSchedule database model — stores predictive service schedules.
=====================================================================
Generated automatically when predictions indicate MEDIUM or HIGH risk.
Maps ML predictions to actionable service workflows.
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID
from datetime import datetime
import uuid

from app.core.database import Base


class ServiceSchedule(Base):
    __tablename__ = "service_schedules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id"),
        nullable=True,
        index=True,
    )
    prediction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("predictions.id"),
        nullable=True,
        index=True,
    )

    # Service configuration
    service_type = Column(
        String, nullable=False, index=True
    )  # "inspection" | "repair" | "urgent"
    priority = Column(
        String, nullable=False, index=True
    )  # "low" | "medium" | "high"
    status = Column(
        String, nullable=False, default="pending", index=True
    )  # "pending" | "scheduled" | "in_progress" | "completed" | "cancelled"

    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)

    # Optional fields
    failure_probability = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)  # Original risk from prediction
    notes = Column(String, nullable=True)
    technician = Column(String, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
