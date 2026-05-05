"""
Master Agent — Orchestrator
=============================
Entry point for the agent workflow.
Coordinates PredictionAgent and ActionAgent in sequence.
Contains NO business logic — pure orchestration only.
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .prediction_agent import PredictionAgent
from .action_agent.action_agent import ActionAgent

logger = logging.getLogger("agents.master")


class MasterAgent:
    """
    Orchestrates the predict-and-act pipeline:
      1. Receive structured sensor input
      2. Delegate to PredictionAgent for ML inference
      3. Pass results to ActionAgent for decision + execution
      4. Return unified response

    This agent contains NO business logic.
    """

    @staticmethod
    async def run(
        features: Dict[str, float],
        vehicle_id: Optional[UUID],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Execute the full predict-and-act pipeline.

        Parameters
        ----------
        features : dict
            Sensor readings: engine_temp, oil_pressure, rpm,
            vibration, battery_voltage, mileage
        vehicle_id : UUID or None
            Optional vehicle identifier for scheduling
        db : AsyncSession
            Database session

        Returns
        -------
        dict — Unified response containing prediction + action results:
            probability       : float
            risk_level        : str (LOW / MEDIUM / HIGH)
            prediction        : int (0 or 1)
            sensor_flags      : list[str]
            threshold_used    : float
            action_taken      : str
            service_scheduled : bool
            service_info      : dict or None
            notification_sent : bool
            reason            : str
        """
        logger.info(
            f"🎯 MasterAgent: Pipeline started | vehicle={vehicle_id}"
        )

        # ─── Step 1: Prediction ───
        prediction_result = PredictionAgent.run(features)

        logger.info(
            f"🎯 MasterAgent: Prediction complete → "
            f"risk={prediction_result['risk_level']}, "
            f"probability={prediction_result['probability']:.4f}"
        )

        # ─── Step 2: Action ───
        action_result = await ActionAgent.execute(
            prediction_result=prediction_result,
            vehicle_id=vehicle_id,
            db=db,
        )

        logger.info(
            f"🎯 MasterAgent: Action complete → "
            f"action={action_result['action_taken']}, "
            f"scheduled={action_result['service_scheduled']}"
        )

        # ─── Step 3: Merge results into unified response ───
        unified_response = {
            **prediction_result,
            **action_result,
        }

        logger.info("🎯 MasterAgent: Pipeline complete ✅")

        return unified_response
