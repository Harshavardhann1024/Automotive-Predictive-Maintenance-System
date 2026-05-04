from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.models.sensor import SensorData, SensorType
from app.models.vehicle import Vehicle
from app.schemas.sensor import (
    SensorDataCreate, SensorDataResponse, SensorDataBatchCreate,
    SensorTypeCreate, SensorTypeResponse, SensorStats, VehicleSensorSummary
)

class SensorService:
    @staticmethod
    async def create_sensor_reading(db: AsyncSession, sensor_data: SensorDataCreate) -> SensorDataResponse:
        """Create a single sensor reading."""
        # Verify vehicle exists
        result = await db.execute(select(Vehicle).where(Vehicle.id == sensor_data.vehicle_id))
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise ValueError(f"Vehicle with ID {sensor_data.vehicle_id} not found")

        # Create sensor reading
        db_sensor_data = SensorData(
            vehicle_id=sensor_data.vehicle_id,
            sensor_type=sensor_data.sensor_type,
            sensor_value=sensor_data.sensor_value,
            unit=sensor_data.unit,
            location=sensor_data.location,
            batch_id=sensor_data.batch_id,
            quality_score=sensor_data.quality_score
        )

        db.add(db_sensor_data)
        await db.commit()
        await db.refresh(db_sensor_data)

        return SensorDataResponse.from_orm(db_sensor_data)

    @staticmethod
    async def create_sensor_readings_batch(db: AsyncSession, batch_data: SensorDataBatchCreate) -> List[SensorDataResponse]:
        """Create multiple sensor readings in a batch."""
        # Verify vehicle exists
        result = await db.execute(select(Vehicle).where(Vehicle.id == batch_data.vehicle_id))
        vehicle = result.scalar_one_or_none()

        if not vehicle:
            raise ValueError(f"Vehicle with ID {batch_data.vehicle_id} not found")

        # Generate batch ID if not provided
        batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{batch_data.vehicle_id}"

        sensor_readings = []
        for reading in batch_data.readings:
            db_sensor_data = SensorData(
                vehicle_id=batch_data.vehicle_id,
                sensor_type=reading.sensor_type,
                sensor_value=reading.sensor_value,
                unit=reading.unit,
                location=reading.location,
                batch_id=batch_id,
                quality_score=reading.quality_score
            )
            sensor_readings.append(db_sensor_data)
            db.add(db_sensor_data)

        await db.commit()

        # Refresh all readings
        for reading in sensor_readings:
            await db.refresh(reading)

        return [SensorDataResponse.from_orm(reading) for reading in sensor_readings]

    @staticmethod
    async def get_sensor_readings(
        db: AsyncSession,
        vehicle_id: Optional[UUID] = None,
        sensor_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[SensorDataResponse]:
        """Get sensor readings with optional filters."""
        query = select(SensorData)

        if vehicle_id:
            query = query.where(SensorData.vehicle_id == vehicle_id)
        if sensor_type:
            query = query.where(SensorData.sensor_type == sensor_type)
        if start_date:
            query = query.where(SensorData.timestamp >= start_date)
        if end_date:
            query = query.where(SensorData.timestamp <= end_date)

        query = query.order_by(desc(SensorData.timestamp)).limit(limit).offset(offset)

        result = await db.execute(query)
        readings = result.scalars().all()

        return [SensorDataResponse.from_orm(reading) for reading in readings]

    @staticmethod
    async def get_sensor_stats(
        db: AsyncSession,
        vehicle_id: Optional[UUID] = None,
        hours: int = 24
    ) -> List[SensorStats]:
        """Get sensor statistics for the specified time period."""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        # Build base query
        query = select(
            SensorData.sensor_type,
            func.count(SensorData.id).label('count'),
            func.avg(SensorData.sensor_value).label('avg_value'),
            func.min(SensorData.sensor_value).label('min_value'),
            func.max(SensorData.sensor_value).label('max_value'),
            func.max(SensorData.timestamp).label('latest_timestamp'),
            func.sum(SensorData.is_anomaly).label('anomaly_count')
        ).where(SensorData.timestamp >= time_threshold)

        if vehicle_id:
            query = query.where(SensorData.vehicle_id == vehicle_id)

        query = query.group_by(SensorData.sensor_type)

        result = await db.execute(query)
        rows = result.all()

        return [
            SensorStats(
                sensor_type=row.sensor_type,
                count=row.count,
                average_value=float(row.avg_value) if row.avg_value else 0.0,
                min_value=float(row.min_value) if row.min_value else 0.0,
                max_value=float(row.max_value) if row.max_value else 0.0,
                latest_timestamp=row.latest_timestamp,
                anomaly_count=row.anomaly_count or 0
            )
            for row in rows
        ]

    @staticmethod
    async def get_vehicle_sensor_summary(db: AsyncSession, vehicle_id: UUID) -> VehicleSensorSummary:
        """Get sensor summary for a specific vehicle."""
        # Get total readings count
        total_query = select(func.count(SensorData.id)).where(SensorData.vehicle_id == vehicle_id)
        total_result = await db.execute(total_query)
        total_readings = total_result.scalar() or 0

        # Get unique sensor types
        sensor_types_query = select(SensorData.sensor_type).where(SensorData.vehicle_id == vehicle_id).distinct()
        sensor_types_result = await db.execute(sensor_types_query)
        sensor_types = [row[0] for row in sensor_types_result.all()]

        # Get latest reading timestamp
        latest_query = select(func.max(SensorData.timestamp)).where(SensorData.vehicle_id == vehicle_id)
        latest_result = await db.execute(latest_query)
        last_reading = latest_result.scalar()

        # Calculate anomaly percentage
        anomaly_query = select(
            func.count(SensorData.id).label('total'),
            func.sum(SensorData.is_anomaly).label('anomalies')
        ).where(SensorData.vehicle_id == vehicle_id)

        anomaly_result = await db.execute(anomaly_query)
        anomaly_row = anomaly_result.first()
        anomaly_percentage = (anomaly_row.anomalies / anomaly_row.total * 100) if anomaly_row.total > 0 else 0.0

        return VehicleSensorSummary(
            vehicle_id=vehicle_id,
            total_readings=total_readings,
            sensor_types=sensor_types,
            last_reading=last_reading,
            anomaly_percentage=round(anomaly_percentage, 2)
        )

    @staticmethod
    async def create_sensor_type(db: AsyncSession, sensor_type_data: SensorTypeCreate) -> SensorTypeResponse:
        """Create a new sensor type definition."""
        # Check if sensor type already exists
        result = await db.execute(select(SensorType).where(SensorType.name == sensor_type_data.name))
        existing_type = result.scalar_one_or_none()

        if existing_type:
            raise ValueError(f"Sensor type '{sensor_type_data.name}' already exists")

        db_sensor_type = SensorType(
            name=sensor_type_data.name,
            description=sensor_type_data.description,
            unit=sensor_type_data.unit,
            normal_range_min=sensor_type_data.normal_range_min,
            normal_range_max=sensor_type_data.normal_range_max,
            critical_threshold=sensor_type_data.critical_threshold
        )

        db.add(db_sensor_type)
        await db.commit()
        await db.refresh(db_sensor_type)

        return SensorTypeResponse.from_orm(db_sensor_type)

    @staticmethod
    async def get_sensor_types(db: AsyncSession) -> List[SensorTypeResponse]:
        """Get all sensor type definitions."""
        result = await db.execute(select(SensorType))
        sensor_types = result.scalars().all()

        return [SensorTypeResponse.from_orm(sensor_type) for sensor_type in sensor_types]