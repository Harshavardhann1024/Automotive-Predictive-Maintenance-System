"""
Predictions Router — ML-powered failure prediction endpoints.
=============================================================
POST /predictions/predict   → Real-time prediction from sensor data
GET  /predictions/history   → Past prediction records
GET  /predictions/stats     → Aggregated risk stats for dashboard
GET  /predictions/model-info → Loaded model metadata

Supports SHAP explainability via ?explain=true query parameter.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.models.prediction import Prediction
from backend.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    PredictionHistoryResponse,
    PredictionStats,
    ModelInfoResponse,
)
from backend.services.ml_service import predict_failure, get_model_info
from backend.services.service_scheduler import generate_service_schedule

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
async def create_prediction(
    data: PredictionRequest,
    background_tasks: BackgroundTasks,
    explain: bool = Query(
        False,
        description="If true, include SHAP feature explanations in response",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Run ML prediction on sensor data.

    Accepts sensor readings, runs through the XGBoost model with
    domain-rule FP filtering, persists the result, and returns
    the prediction with risk level.

    Pass ?explain=true to include SHAP-based feature explanations
    (adds ~5-20ms to response time on first call, <5ms thereafter).

    After storing the prediction, the service scheduler is triggered
    asynchronously to generate service tasks for MEDIUM/HIGH risk results.
    """
    try:
        features = {
            "engine_temp": data.engine_temp,
            "oil_pressure": data.oil_pressure,
            "rpm": data.rpm,
            "vibration": data.vibration,
            "battery_voltage": data.battery_voltage,
            "mileage": data.mileage,
        }

        result = predict_failure(features, explain=explain)

        # Persist to database (core fields only, SHAP is transient)
        db_prediction = Prediction(
            vehicle_id=data.vehicle_id,
            engine_temp=data.engine_temp,
            oil_pressure=data.oil_pressure,
            rpm=data.rpm,
            vibration=data.vibration,
            battery_voltage=data.battery_voltage,
            mileage=data.mileage,
            failure_probability=result["failure_probability"],
            prediction=result["prediction"],
            risk_level=result["risk_level"],
            threshold_used=result["threshold_used"],
        )
        db.add(db_prediction)
        await db.commit()
        await db.refresh(db_prediction)

        # ─── Trigger Service Scheduler (non-blocking) ───
        try:
            schedule_result = await generate_service_schedule(
                db=db,
                vehicle_id=data.vehicle_id,
                prediction_id=db_prediction.id,
                risk_level=result["risk_level"],
                failure_probability=result["failure_probability"],
                background_tasks=background_tasks,
            )
            if schedule_result:
                await db.commit()
        except Exception as sched_err:
            # Scheduler failure should NOT block the prediction response
            import logging
            logging.getLogger("routers.predictions").warning(
                f"Service scheduler error (non-blocking): {sched_err}"
            )

        return PredictionResponse(**result)

    except KeyError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required sensor field: {e}",
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )


@router.get("/history", response_model=List[PredictionHistoryResponse])
async def get_prediction_history(
    vehicle_id: Optional[UUID] = Query(None, description="Filter by vehicle ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (Low/Medium/High)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get historical prediction records with optional filters."""
    try:
        query = select(Prediction)

        if vehicle_id:
            query = query.where(Prediction.vehicle_id == vehicle_id)
        if risk_level:
            query = query.where(Prediction.risk_level == risk_level)

        query = query.order_by(desc(Prediction.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        predictions = result.scalars().all()

        return [PredictionHistoryResponse.model_validate(p) for p in predictions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=PredictionStats)
async def get_prediction_stats(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated prediction statistics for dashboard cards."""
    try:
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        # Total predictions in window
        total_q = select(func.count(Prediction.id)).where(
            Prediction.created_at >= time_threshold
        )
        total_result = await db.execute(total_q)
        total = total_result.scalar() or 0

        # Risk level counts
        high_q = select(func.count(Prediction.id)).where(
            Prediction.created_at >= time_threshold,
            Prediction.risk_level == "High",
        )
        medium_q = select(func.count(Prediction.id)).where(
            Prediction.created_at >= time_threshold,
            Prediction.risk_level == "Medium",
        )
        low_q = select(func.count(Prediction.id)).where(
            Prediction.created_at >= time_threshold,
            Prediction.risk_level == "Low",
        )

        high_result = await db.execute(high_q)
        medium_result = await db.execute(medium_q)
        low_result = await db.execute(low_q)

        high_count = high_result.scalar() or 0
        medium_count = medium_result.scalar() or 0
        low_count = low_result.scalar() or 0

        # Average failure probability
        avg_q = select(func.avg(Prediction.failure_probability)).where(
            Prediction.created_at >= time_threshold
        )
        avg_result = await db.execute(avg_q)
        avg_prob = avg_result.scalar() or 0.0

        # Failure rate (prediction == 1)
        failure_q = select(func.count(Prediction.id)).where(
            Prediction.created_at >= time_threshold,
            Prediction.prediction == 1,
        )
        failure_result = await db.execute(failure_q)
        failure_count = failure_result.scalar() or 0

        return PredictionStats(
            total_predictions=total,
            high_risk_count=high_count,
            medium_risk_count=medium_count,
            low_risk_count=low_count,
            avg_failure_probability=round(float(avg_prob), 4),
            recent_failure_rate=round(failure_count / total, 4) if total > 0 else 0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_ml_model_info():
    """Return metadata about the currently loaded ML model."""
    try:
        info = get_model_info()
        return ModelInfoResponse(**info)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
