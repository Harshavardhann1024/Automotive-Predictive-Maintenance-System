from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.services.sensor_service import SensorService
from app.routers.auth import get_current_active_user

router = APIRouter()

@router.get("/")
async def list_alerts(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """List all recent anomaly alerts."""
    try:
        # Re-using visualization logic or service logic for alerts
        start_date = datetime.utcnow() - timedelta(hours=hours)
        readings = await SensorService.get_sensor_readings(
            db=db,
            start_date=start_date,
            limit=limit * 5 # Get more to filter
        )
        
        anomalies = [r for r in readings if r.is_anomaly > 0]
        
        alerts = []
        for r in anomalies[:limit]:
            alerts.append({
                "id": str(r.id),
                "vehicle_id": str(r.vehicle_id),
                "sensor_type": r.sensor_type,
                "value": r.sensor_value,
                "unit": r.unit,
                "timestamp": r.timestamp.isoformat(),
                "severity": "high" if r.is_anomaly > 1 else "medium",
                "status": "Active" # Mock status
            })
            
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Acknowledge an alert."""
    return {"message": f"Alert {alert_id} acknowledged", "status": "Acknowledged"}

@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Resolve an alert."""
    return {"message": f"Alert {alert_id} resolved", "status": "Resolved"}
