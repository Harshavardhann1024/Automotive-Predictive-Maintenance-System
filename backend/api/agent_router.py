"""
Agent Router — Agent-based predict-and-act endpoint
=====================================================
POST /agents/predict-and-act  → Full pipeline: predict + decide + act
GET  /agents/health           → Agent system health check
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.models.prediction import Prediction
from backend.schemas.agent import AgentPredictRequest, AgentPredictResponse
from backend.agents.master_agent import MasterAgent

logger = logging.getLogger("routers.agents")

router = APIRouter()


@router.post("/predict-and-act", response_model=AgentPredictResponse)
async def predict_and_act(
    data: AgentPredictRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Full agent pipeline: Predict failure and take action.

    Flow:
    1. MasterAgent receives sensor input
    2. PredictionAgent runs ML inference (reusing existing ML service)
    3. ActionAgent decides action, schedules service if needed, notifies
    4. Returns unified response with prediction + action results

    Example request:
    ```json
    {
        "engine_temp": 115.0,
        "oil_pressure": 28.0,
        "rpm": 3500,
        "vibration": 0.85,
        "battery_voltage": 11.5,
        "mileage": 95000,
        "vehicle_id": "optional-uuid-here"
    }
    ```
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

        logger.info(
            f"📨 /agents/predict-and-act | vehicle={data.vehicle_id} | "
            f"engine_temp={data.engine_temp}, oil_pressure={data.oil_pressure}"
        )

        # ─── Run the Master Agent pipeline ───
        result = await MasterAgent.run(
            features=features,
            vehicle_id=data.vehicle_id,
            db=db,
            background_tasks=background_tasks,
        )

        # ─── Also persist the prediction to the existing predictions table ───
        db_prediction = Prediction(
            vehicle_id=data.vehicle_id,
            engine_temp=data.engine_temp,
            oil_pressure=data.oil_pressure,
            rpm=data.rpm,
            vibration=data.vibration,
            battery_voltage=data.battery_voltage,
            mileage=data.mileage,
            failure_probability=result["probability"],
            prediction=result["prediction"],
            risk_level=result["risk_level"],
            threshold_used=result["threshold_used"],
        )
        db.add(db_prediction)
        await db.commit()

        logger.info(
            f"📨 /agents/predict-and-act | Response: "
            f"risk={result['risk_level']}, action={result['action_taken']}, "
            f"scheduled={result['service_scheduled']}"
        )

        return AgentPredictResponse(**result)

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
        logger.exception("Agent pipeline failed")
        raise HTTPException(
            status_code=500,
            detail=f"Agent pipeline failed: {str(e)}",
        )


@router.get("/health")
async def agent_health():
    """Health check for the agent subsystem."""
    return {
        "status": "healthy",
        "agents": [
            {"name": "MasterAgent", "role": "orchestrator", "status": "active"},
            {"name": "PredictionAgent", "role": "ml_inference", "status": "active"},
            {"name": "ActionAgent", "role": "decision_execution", "status": "active"},
        ],
        "components": [
            {"name": "DecisionEngine", "parent": "ActionAgent", "status": "active"},
            {"name": "Scheduler", "parent": "ActionAgent", "status": "active"},
            {"name": "Notifier", "parent": "ActionAgent", "status": "active"},
        ],
    }
