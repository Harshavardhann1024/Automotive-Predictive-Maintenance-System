"""
Notifier — Structured Notification Dispatcher
===============================================
Currently uses structured logging to simulate notifications.
Designed for future extensibility (email, SMS, push, webhooks).
"""

import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from enum import Enum

logger = logging.getLogger("agents.action.notifier")


class NotificationChannel(str, Enum):
    """Supported notification channels (for future extensibility)."""
    LOG = "LOG"
    EMAIL = "EMAIL"       # Future
    SMS = "SMS"           # Future
    PUSH = "PUSH"         # Future
    WEBHOOK = "WEBHOOK"   # Future


class NotificationPriority(str, Enum):
    """Notification urgency levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Notifier:
    """
    Dispatches notifications via structured logging.
    Designed as an extensible notification gateway.
    """

    # Map risk levels to notification priority
    _PRIORITY_MAP = {
        "LOW": NotificationPriority.INFO,
        "MEDIUM": NotificationPriority.WARNING,
        "HIGH": NotificationPriority.CRITICAL,
    }

    @classmethod
    def send(
        cls,
        risk_level: str,
        probability: float,
        vehicle_id: Optional[UUID] = None,
        sensor_flags: Optional[List[str]] = None,
        action_taken: str = "NOTIFY",
        service_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Dispatch a notification for a prediction result.

        Parameters
        ----------
        risk_level : str
            The risk classification (LOW / MEDIUM / HIGH)
        probability : float
            Failure probability
        vehicle_id : UUID, optional
            Vehicle identifier
        sensor_flags : list[str], optional
            List of triggered domain rules
        action_taken : str
            The action that was taken
        service_info : dict, optional
            Service scheduling details (if applicable)

        Returns
        -------
        dict with notification delivery status
        """
        priority = cls._PRIORITY_MAP.get(risk_level, NotificationPriority.INFO)
        channel = NotificationChannel.LOG  # Current implementation

        notification_payload = {
            "channel": channel.value,
            "priority": priority.value,
            "risk_level": risk_level,
            "probability": probability,
            "vehicle_id": str(vehicle_id) if vehicle_id else None,
            "sensor_flags": sensor_flags or [],
            "action_taken": action_taken,
            "service_info": service_info,
        }

        # ─── Structured log output (simulates notification dispatch) ───
        cls._log_notification(notification_payload, priority)

        return {
            "notification_sent": True,
            "channel": channel.value,
            "priority": priority.value,
        }

    @staticmethod
    def _log_notification(payload: Dict[str, Any], priority: NotificationPriority) -> None:
        """Emit structured log as notification simulation."""
        vehicle_str = payload.get("vehicle_id") or "UNKNOWN"
        risk = payload["risk_level"]
        prob = payload["probability"]
        action = payload["action_taken"]
        flags = ", ".join(payload.get("sensor_flags", [])) or "none"

        message = (
            f"🔔 NOTIFICATION [{priority.value}] | "
            f"Vehicle: {vehicle_str} | "
            f"Risk: {risk} (p={prob:.4f}) | "
            f"Action: {action} | "
            f"Sensor flags: [{flags}]"
        )

        if payload.get("service_info"):
            svc = payload["service_info"]
            message += (
                f" | Service: id={svc.get('service_request_id', 'N/A')}, "
                f"scheduled={svc.get('scheduled_time', 'N/A')}"
            )

        if priority == NotificationPriority.CRITICAL:
            logger.critical(message)
        elif priority == NotificationPriority.WARNING:
            logger.warning(message)
        else:
            logger.info(message)
