from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.services.sensor_service import SensorService
from app.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/sensor-trends/{vehicle_id}")
async def get_sensor_trends(
    vehicle_id: UUID,
    sensor_type: str = Query(..., description="Sensor type to visualize"),
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get sensor data trends for visualization."""
    try:
        # Get sensor readings
        start_date = datetime.utcnow() - timedelta(hours=hours)
        readings = await SensorService.get_sensor_readings(
            db=db,
            vehicle_id=vehicle_id,
            sensor_type=sensor_type,
            start_date=start_date,
            limit=1000
        )

        if not readings:
            return JSONResponse(
                content={
                    "message": f"No data found for sensor type '{sensor_type}' in the last {hours} hours",
                    "data": []
                }
            )

        # Prepare data for visualization
        timestamps = [reading.timestamp.isoformat() for reading in readings]
        values = [reading.sensor_value for reading in readings]
        anomalies = [reading.is_anomaly for reading in readings]

        chart_data = {
            "timestamps": timestamps,
            "values": values,
            "anomalies": anomalies,
            "sensor_type": sensor_type,
            "unit": readings[0].unit if readings else "unknown",
            "total_points": len(readings),
            "anomaly_count": sum(anomalies)
        }

        return JSONResponse(content=chart_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/vehicle-overview/{vehicle_id}")
async def get_vehicle_overview(
    vehicle_id: UUID,
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get comprehensive vehicle sensor overview for dashboard."""
    try:
        # Get sensor stats
        stats = await SensorService.get_sensor_stats(db, vehicle_id, hours)

        # Get vehicle summary
        summary = await SensorService.get_vehicle_sensor_summary(db, vehicle_id)

        if not stats:
            return JSONResponse(
                content={
                    "message": f"No sensor data found for vehicle in the last {hours} hours",
                    "summary": summary.dict(),
                    "charts": []
                }
            )

        # Prepare dashboard data
        dashboard_data = {
            "summary": summary.dict(),
            "sensor_stats": [stat.dict() for stat in stats],
            "charts": {
                "sensor_types": [stat.sensor_type for stat in stats],
                "reading_counts": [stat.count for stat in stats],
                "anomaly_counts": [stat.anomaly_count for stat in stats],
                "average_values": [stat.average_value for stat in stats]
            },
            "time_range": f"{hours} hours",
            "generated_at": datetime.utcnow().isoformat()
        }

        return JSONResponse(content=dashboard_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/fleet-overview")
async def get_fleet_overview(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get fleet-wide sensor overview."""
    try:
        # Get overall sensor stats
        stats = await SensorService.get_sensor_stats(db, None, hours)

        if not stats:
            return JSONResponse(
                content={
                    "message": f"No sensor data found in the last {hours} hours",
                    "fleet_summary": {
                        "total_vehicles": 0,
                        "total_readings": 0,
                        "total_anomalies": 0
                    },
                    "charts": []
                }
            )

        # Calculate fleet summary
        total_readings = sum(stat.count for stat in stats)
        total_anomalies = sum(stat.anomaly_count for stat in stats)

        # Get unique vehicles count (this is approximate)
        vehicles_query = """
        SELECT COUNT(DISTINCT vehicle_id) as vehicle_count
        FROM sensor_data
        WHERE timestamp >= $1
        """
        # Note: This would need proper implementation with raw SQL or additional service method

        fleet_data = {
            "fleet_summary": {
                "total_readings": total_readings,
                "total_anomalies": total_anomalies,
                "anomaly_rate": round((total_anomalies / total_readings * 100), 2) if total_readings > 0 else 0,
                "sensor_types_count": len(stats)
            },
            "sensor_breakdown": [stat.dict() for stat in stats],
            "charts": {
                "sensor_types": [stat.sensor_type for stat in stats],
                "total_readings": [stat.count for stat in stats],
                "anomaly_rates": [
                    round((stat.anomaly_count / stat.count * 100), 2) if stat.count > 0 else 0
                    for stat in stats
                ]
            },
            "time_range": f"{hours} hours",
            "generated_at": datetime.utcnow().isoformat()
        }

        return JSONResponse(content=fleet_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/anomaly-alerts")
async def get_anomaly_alerts(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours"),
    limit: int = Query(50, ge=1, le=200, description="Maximum alerts to return"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get recent anomaly alerts for monitoring."""
    try:
        # Get sensor readings with anomalies
        start_date = datetime.utcnow() - timedelta(hours=hours)
        readings = await SensorService.get_sensor_readings(
            db=db,
            start_date=start_date,
            limit=limit * 2  # Get more to filter anomalies
        )

        # Filter for anomalies
        anomaly_readings = [r for r in readings if r.is_anomaly > 0]

        alerts = []
        for reading in anomaly_readings[:limit]:
            alerts.append({
                "id": str(reading.id),
                "vehicle_id": str(reading.vehicle_id),
                "sensor_type": reading.sensor_type,
                "value": reading.sensor_value,
                "unit": reading.unit,
                "location": reading.location,
                "timestamp": reading.timestamp.isoformat(),
                "severity": "high" if reading.is_anomaly > 1 else "medium"
            })

        return JSONResponse(content={
            "alerts": alerts,
            "total_alerts": len(anomaly_readings),
            "time_range": f"{hours} hours",
            "generated_at": datetime.utcnow().isoformat()
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")