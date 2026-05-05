"""
Decision Engine — Risk-based action routing
=============================================
Maps risk levels to concrete actions:
  LOW    → LOG_ONLY
  MEDIUM → NOTIFY
  HIGH   → NOTIFY + SERVICE_SCHEDULED
"""

import logging
from enum import Enum
from typing import Dict, Any

logger = logging.getLogger("agents.action.decision")


class ActionType(str, Enum):
    """Possible actions the system can take."""
    LOG_ONLY = "LOG_ONLY"
    NOTIFY = "NOTIFY"
    SERVICE_SCHEDULED = "SERVICE_SCHEDULED"


class DecisionEngine:
    """
    Stateless decision mapper.
    Takes a risk level and returns the appropriate action.
    """

    # ─── Decision matrix ───
    _DECISION_MAP: Dict[str, ActionType] = {
        "LOW": ActionType.LOG_ONLY,
        "MEDIUM": ActionType.NOTIFY,
        "HIGH": ActionType.SERVICE_SCHEDULED,
    }

    @classmethod
    def decide(cls, risk_level: str, probability: float) -> Dict[str, Any]:
        """
        Determine the action to take based on risk level.

        Parameters
        ----------
        risk_level : str
            One of "LOW", "MEDIUM", "HIGH"
        probability : float
            Failure probability from the prediction agent

        Returns
        -------
        dict with:
            action_type     : ActionType enum value
            should_notify   : bool
            should_schedule : bool
            reason          : str (human-readable explanation)
        """
        action = cls._DECISION_MAP.get(risk_level, ActionType.LOG_ONLY)

        should_notify = action in (ActionType.NOTIFY, ActionType.SERVICE_SCHEDULED)
        should_schedule = action == ActionType.SERVICE_SCHEDULED

        reason = cls._build_reason(risk_level, probability, action)

        logger.info(
            f"⚖️  DecisionEngine: risk={risk_level} | probability={probability:.4f} → "
            f"action={action.value} | notify={should_notify} | schedule={should_schedule}"
        )

        return {
            "action_type": action,
            "should_notify": should_notify,
            "should_schedule": should_schedule,
            "reason": reason,
        }

    @staticmethod
    def _build_reason(risk_level: str, probability: float, action: ActionType) -> str:
        """Generate a human-readable reason for the decision."""
        reasons = {
            ActionType.LOG_ONLY: (
                f"Risk level {risk_level} (p={probability:.4f}) — "
                "within normal parameters. Logged for monitoring."
            ),
            ActionType.NOTIFY: (
                f"Risk level {risk_level} (p={probability:.4f}) — "
                "elevated risk detected. Notification dispatched."
            ),
            ActionType.SERVICE_SCHEDULED: (
                f"Risk level {risk_level} (p={probability:.4f}) — "
                "critical risk detected. Service appointment scheduled and notification sent."
            ),
        }
        return reasons.get(action, "Unknown decision state.")
