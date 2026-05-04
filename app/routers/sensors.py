from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.services.sensor_service import SensorService
from app.schemas.sensor import (
    SensorDataCreate, SensorDataResponse, SensorDataBatchCreate,
    SensorTypeCreate, SensorTypeResponse, SensorStats, VehicleSensorSummary
)
from app.routers.auth import get_current_active_user

router = APIRouter()

@router.post("/readings", response_model=SensorDataResponse)
async def create_sensor_reading(
    sensor_data: SensorDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a single sensor reading."""
    try:
        reading = await SensorService.create_sensor_reading(db, sensor_data)
        return reading
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/readings/batch", response_model=List[SensorDataResponse])
async def create_sensor_readings_batch(
    batch_data: SensorDataBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create multiple sensor readings in a batch."""
    try:
        readings = await SensorService.create_sensor_readings_batch(db, batch_data)
        return readings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/readings", response_model=List[SensorDataResponse])
async def get_sensor_readings(
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle ID"),
    sensor_type: Optional[str] = Query(None, description="Filter by sensor type"),
    limit: int = Query(100, ge=1, le=1000, description="Number of readings to return"),
    offset: int = Query(0, ge=0, description="Number of readings to skip"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get sensor readings with optional filters."""
    try:
        readings = await SensorService.get_sensor_readings(
            db=db,
            vehicle_id=vehicle_id,
            sensor_type=sensor_type,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        return readings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/stats", response_model=List[SensorStats])
async def get_sensor_stats(
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle ID"),
    hours: int = Query(24, ge=1, le=168, description="Time period in hours (max 1 week)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get sensor statistics for the specified time period."""
    try:
        stats = await SensorService.get_sensor_stats(db, vehicle_id, hours)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/vehicles/{vehicle_id}/summary", response_model=VehicleSensorSummary)
async def get_vehicle_sensor_summary(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get sensor summary for a specific vehicle."""
    try:
        summary = await SensorService.get_vehicle_sensor_summary(db, vehicle_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/types", response_model=SensorTypeResponse)
async def create_sensor_type(
    sensor_type_data: SensorTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Create a new sensor type definition."""
    try:
        sensor_type = await SensorService.create_sensor_type(db, sensor_type_data)
        return sensor_type
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/types", response_model=List[SensorTypeResponse])
async def get_sensor_types(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get all sensor type definitions."""
    try:
        sensor_types = await SensorService.get_sensor_types(db)
        return sensor_types
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")