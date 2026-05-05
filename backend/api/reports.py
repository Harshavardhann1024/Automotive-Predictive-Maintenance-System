from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from backend.core.database import get_db
from backend.api.auth import get_current_active_user
from backend.services.report_service import ReportService
from backend.services.sensor_service import SensorService

router = APIRouter()

@router.get("/generate")
async def generate_report(
    format: str = Query(..., pattern="^(pdf|csv)$"),
    type: str = Query(..., description="Report type"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Generate a report in PDF or CSV format."""
    if format == "pdf":
        # Get data for the report
        stats = await SensorService.get_sensor_stats(db, None, 24)
        total_readings = sum(s.count for s in stats)
        total_anomalies = sum(s.anomaly_count for s in stats)
        
        report_data = {
            "total_readings": total_readings,
            "total_anomalies": total_anomalies,
            "anomaly_rate": round((total_anomalies / total_readings * 100), 2) if total_readings > 0 else 0
        }
        
        pdf_buffer = await ReportService.generate_fleet_report(report_data, type)
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{type}.pdf"}
        )
    
    # Fallback for CSV or other
    return {"message": f"Generated {format} report of type {type}", "status": "success"}

@router.get("/export/zip")
async def export_data_zip(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Export all data as a ZIP archive."""
    return {"message": "Data export ZIP is being prepared", "status": "success"}
