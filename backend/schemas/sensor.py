from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class SensorDataCreate(BaseModel):
    vehicle_id: UUID
    sensor_type: str = Field(..., description="Type of sensor (temperature, vibration, pressure, etc.)")
    sensor_value: float = Field(..., description="The sensor reading value")
    unit: str = Field(..., description="Unit of measurement (celsius, hz, psi, etc.)")
    location: Optional[str] = Field(None, description="Location on the vehicle (engine, transmission, etc.)")
    batch_id: Optional[str] = Field(None, description="Batch ID for grouping related readings")
    quality_score: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Data quality score")

class SensorDataResponse(BaseModel):
    id: UUID
    vehicle_id: UUID
    sensor_type: str
    sensor_value: float
    unit: str
    location: Optional[str]
    timestamp: datetime
    batch_id: Optional[str]
    quality_score: float
    is_anomaly: int

    class Config:
        from_attributes = True

class SensorDataBatchCreate(BaseModel):
    vehicle_id: UUID
    readings: List[SensorDataCreate] = Field(..., description="List of sensor readings in this batch")

class SensorTypeCreate(BaseModel):
    name: str
    description: Optional[str]
    unit: str
    normal_range_min: Optional[float]
    normal_range_max: Optional[float]
    critical_threshold: Optional[float]

class SensorTypeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    unit: str
    normal_range_min: Optional[float]
    normal_range_max: Optional[float]
    critical_threshold: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class SensorStats(BaseModel):
    sensor_type: str
    count: int
    average_value: float
    min_value: float
    max_value: float
    latest_timestamp: datetime
    anomaly_count: int

class VehicleSensorSummary(BaseModel):
    vehicle_id: UUID
    total_readings: int
    sensor_types: List[str]
    last_reading: Optional[datetime]
    anomaly_percentage: float