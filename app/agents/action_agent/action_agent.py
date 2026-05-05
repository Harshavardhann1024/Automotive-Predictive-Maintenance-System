"""
Action Agent — Execution Layer
================================
Coordinates the decision engine, scheduler, and notifier.
Receives prediction results and executes the appropriate actions:
  - Makes a decision based on risk level
  - Schedules service if required
  - Sends notifications when needed
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .decision_engine import DecisionEngine, ActionType
from .scheduler import Scheduler
from .notifier import Notifier

logger = logging.getLogger("agents.action")


class ActionAgent:
    """
    Execution layer that processes prediction results and takes appropriate
    actions based on the decision engine's output.
    """

    @staticmethod
    async def execute(
        prediction_result: Dict[str, Any],
        vehicle_id: Optional[UUID],
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Execute actions based on a prediction result.

        Parameters
        ----------
        prediction_result : dict
            Output from PredictionAgent.run() containing:
            probability, risk_level, prediction, sensor_flags, threshold_used
        vehicle_id : UUID or None
            Vehicle to take action on
        db : AsyncSession
            Database session for service scheduling

        Returns
        -------
        dict with:
            action_taken     : str (action type value)
            service_scheduled: bool
            service_info     : dict or None
            notification_sent: bool
            reason           : str
        """
        risk_level = prediction_result["risk_level"]
        probability = prediction_result["probability"]
        sensor_flags = prediction_result.get("sensor_flags", [])

        logger.info(
            f"⚡ ActionAgent: Processing | risk={risk_level}, "
            f"probability={probability:.4f}, vehicle={vehicle_id}"
        )

        # ─── Step 1: Decision ───
        decision = DecisionEngine.decide(risk_level, probability)
        action_type: ActionType = decision["action_type"]

        # ─── Step 2: Schedule service if required ───
        service_info = None
        service_scheduled = False

        if decision["should_schedule"] and vehicle_id is not None:
            try:
                service_info = await Scheduler.schedule_service(
                    db=db,
                    vehicle_id=vehicle_id,
                    risk_level=risk_level,
                )
                service_scheduled = True
                logger.info(
                    f"⚡ ActionAgent: Service scheduled | "
                    f"request_id={service_info['service_request_id']}"
                )
            except Exception as e:
                logger.error(f"⚡ ActionAgent: Scheduling failed | error={e}")
                # Downgrade to notification-only if scheduling fails
                service_info = {"error": str(e)}
        elif decision["should_schedule"] and vehicle_id is None:
            logger.warning(
                "⚡ ActionAgent: Scheduling skipped — no vehicle_id provided"
            )

        # ─── Step 3: Notify if required ───
        notification_result = {"notification_sent": False}

        if decision["should_notify"]:
            notification_result = Notifier.send(
                risk_level=risk_level,
                probability=probability,
                vehicle_id=vehicle_id,
                sensor_flags=sensor_flags,
                action_taken=action_type.value,
                service_info=service_info,
            )

        # ─── Build response ───
        result = {
            "action_taken": action_type.value,
            "service_scheduled": service_scheduled,
            "service_info": service_info if service_scheduled else None,
            "notification_sent": notification_result.get("notification_sent", False),
            "reason": decision["reason"],
        }

        logger.info(
            f"⚡ ActionAgent: Complete | action={action_type.value}, "
            f"scheduled={service_scheduled}, notified={result['notification_sent']}"
        )

        return result
