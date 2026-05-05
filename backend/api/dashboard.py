from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.services.sensor_service import SensorService
from backend.services.report_service import ReportService
from backend.api.auth import get_current_active_user
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/api/dashboard/summary")
async def get_dashboard_summary(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Get fleet summary KPIs for the dashboard."""
    try:
        stats = await SensorService.get_sensor_stats(db, None, hours)
        
        total_readings = sum(s.count for s in stats)
        total_anomalies = sum(s.anomaly_count for s in stats)
        
        return {
            "total_readings": total_readings,
            "total_anomalies": total_anomalies,
            "anomaly_rate": round((total_anomalies / total_readings * 100), 2) if total_readings > 0 else 0,
            "sensor_types_count": len(stats),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_dashboard_report(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Generate executive PDF report."""
    stats = await SensorService.get_sensor_stats(db, None, 24)
    total_readings = sum(s.count for s in stats)
    total_anomalies = sum(s.anomaly_count for s in stats)
    
    report_data = {
        "total_readings": total_readings,
        "total_anomalies": total_anomalies,
        "anomaly_rate": round((total_anomalies / total_readings * 100), 2) if total_readings > 0 else 0
    }
    
    pdf_buffer = await ReportService.generate_fleet_report(report_data, "Executive Dashboard Summary")
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=executive_report.pdf"}
    )
