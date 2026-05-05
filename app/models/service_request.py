"""
ServiceRequest database model — stores scheduled service appointments.
======================================================================
Created by the Action Agent's Scheduler when HIGH risk is detected.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID
from datetime import datetime
import uuid

from app.core.database import Base


class ServiceRequest(Base):
    __tablename__ = "service_requests"

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

    # Risk context
    risk_level = Column(String, nullable=False)  # LOW / MEDIUM / HIGH

    # User Decision tracking
    user_decision = Column(String, nullable=True)  # APPROVE_SERVICE / REMIND_LATER / IGNORE_ALERT
    decision_timestamp = Column(DateTime, nullable=True)

    # Scheduling
    scheduled_time = Column(DateTime, nullable=True, index=True)
    status = Column(
        String,
        nullable=False,
        default="PENDING",
        index=True,
    )  # PENDING / SCHEDULED / CANCELLED / DEFERRED

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
