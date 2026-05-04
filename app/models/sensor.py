from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy import Uuid as UUID
from datetime import datetime
import uuid

from app.core.database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    sensor_type = Column(String, nullable=False)  # e.g., "temperature", "vibration", "pressure"
    sensor_value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # e.g., "celsius", "hz", "psi"
    location = Column(String)  # e.g., "engine", "transmission", "brakes"
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    batch_id = Column(String, index=True)  # For grouping related readings

    # Additional metadata
    quality_score = Column(Float, default=1.0)  # Data quality indicator (0-1)
    is_anomaly = Column(Integer, default=0)  # Flag for detected anomalies

class SensorType(Base):
    __tablename__ = "sensor_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    unit = Column(String, nullable=False)
    normal_range_min = Column(Float)
    normal_range_max = Column(Float)
    critical_threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)