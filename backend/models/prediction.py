"""
Prediction database model — stores ML prediction results.
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID
from datetime import datetime
import uuid

from backend.core.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True, index=True)

    # Sensor inputs (snapshot at prediction time)
    engine_temp = Column(Float, nullable=False)
    oil_pressure = Column(Float, nullable=False)
    rpm = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    battery_voltage = Column(Float, nullable=False)
    mileage = Column(Float, nullable=False)

    # ML outputs
    failure_probability = Column(Float, nullable=False)
    prediction = Column(Integer, nullable=False)       # 0 or 1
    risk_level = Column(String, nullable=False)         # Low / Medium / High
    threshold_used = Column(Float, nullable=False)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
