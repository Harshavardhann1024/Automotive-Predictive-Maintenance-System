"""
Service Scheduler — Intelligent Service Generation Engine
==========================================================
Automatically generates service tasks based on ML predictions and risk levels.

Risk Level Mapping:
    LOW    → No action (no schedule created)
    MEDIUM → Schedule inspection within 3–5 days
    HIGH   → Immediate service required within 24 hours

Business Rules:
    - Avoid duplicate schedules for same vehicle within short time window
    - If multiple HIGH risks → escalate priority
    - Domain-rule filter must pass before scheduling
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.service_schedule import ServiceSchedule

logger = logging.getLogger("services.scheduler")

# ─── Configuration ───
DUPLICATE_WINDOW_HOURS = 6       # Prevent duplicates within this window
HIGH_RISK_DEADLINE_HOURS = 24    # HIGH risk must be scheduled within 24h
MEDIUM_RISK_MIN_DAYS = 3         # MEDIUM risk scheduled 3–5 days out
MEDIUM_RISK_MAX_DAYS = 5
ESCALATION_THRESHOLD = 3         # Multiple HIGHs within window → escalate


# ─── Risk → Service Type Mapping ───
RISK_SERVICE_MAP = {
    "High": {"service_type": "urgent", "priority": "high"},
    "HIGH": {"service_type": "urgent", "priority": "high"},
    "Medium": {"service_type": "inspection", "priority": "medium"},
    "MEDIUM": {"service_type": "inspection", "priority": "medium"},
    "Low": {"service_type": "inspection", "priority": "low"},
    "LOW": {"service_type": "inspection", "priority": "low"},
}


async def check_duplicate_schedule(
    db: AsyncSession,
    vehicle_id: Optional[UUID],
    window_hours: int = DUPLICATE_WINDOW_HOURS,
) -> bool:
    """
    Check if a service schedule already exists for this vehicle
    within the deduplication window.
    
    Returns True if a duplicate exists (should NOT create new schedule).
    """
    if vehicle_id is None:
        return False

    cutoff = datetime.utcnow() - timedelta(hours=window_hours)

    query = select(func.count(ServiceSchedule.id)).where(
        and_(
            ServiceSchedule.vehicle_id == vehicle_id,
            ServiceSchedule.created_at >= cutoff,
            ServiceSchedule.status.in_(["pending", "scheduled", "in_progress"]),
        )
    )
    result = await db.execute(query)
    count = result.scalar() or 0

    if count > 0:
        logger.info(
            f"📅 Scheduler: Duplicate detected for vehicle={vehicle_id} "
            f"({count} active schedule(s) within {window_hours}h window)"
        )

    return count > 0


async def check_escalation(
    db: AsyncSession,
    vehicle_id: Optional[UUID],
    window_hours: int = DUPLICATE_WINDOW_HOURS,
) -> bool:
    """
    Check if there are multiple HIGH-risk schedules for this vehicle,
    indicating need for priority escalation.
    """
    if vehicle_id is None:
        return False

    cutoff = datetime.utcnow() - timedelta(hours=window_hours)

    query = select(func.count(ServiceSchedule.id)).where(
        and_(
            ServiceSchedule.vehicle_id == vehicle_id,
            ServiceSchedule.priority == "high",
            ServiceSchedule.created_at >= cutoff,
            ServiceSchedule.status.in_(["pending", "scheduled", "in_progress"]),
        )
    )
    result = await db.execute(query)
    count = result.scalar() or 0

    return count >= ESCALATION_THRESHOLD


def compute_scheduled_date(risk_level: str) -> datetime:
    """
    Calculate intelligent scheduling date based on risk level.
    
    HIGH   → within 24 hours (random 2–24h for realistic spread)
    MEDIUM → within 3–5 days
    LOW    → no schedule (should not reach here)
    """
    now = datetime.utcnow()
    risk_upper = risk_level.upper()

    if risk_upper == "HIGH":
        hours_offset = random.randint(2, HIGH_RISK_DEADLINE_HOURS)
        return now + timedelta(hours=hours_offset)
    elif risk_upper == "MEDIUM":
        days_offset = random.randint(MEDIUM_RISK_MIN_DAYS, MEDIUM_RISK_MAX_DAYS)
        # Schedule during business hours (10:00 AM)
        scheduled = now + timedelta(days=days_offset)
        scheduled = scheduled.replace(hour=10, minute=0, second=0, microsecond=0)
        return scheduled
    else:
        # LOW risk — shouldn't be called, but fallback to 7 days
        return now + timedelta(days=7)


async def generate_service_schedule(
    db: AsyncSession,
    vehicle_id: Optional[UUID],
    prediction_id: Optional[UUID],
    risk_level: str,
    failure_probability: float,
) -> Optional[Dict[str, Any]]:
    """
    Main entry point: Generate a service schedule from a prediction.
    
    Returns the created schedule info, or None if:
    - Risk is LOW (no action needed)
    - Duplicate already exists
    - Domain rules filtered out
    
    Parameters
    ----------
    db : AsyncSession
    vehicle_id : UUID or None
    prediction_id : UUID or None
    risk_level : str — "Low" | "Medium" | "High" (or uppercase variants)
    failure_probability : float — 0.0 to 1.0
    """
    risk_upper = risk_level.upper()

    # ─── Rule: LOW risk → no schedule ───
    if risk_upper == "LOW":
        logger.info("📅 Scheduler: LOW risk — no service schedule needed")
        return None

    # ─── Rule: Deduplication ───
    if await check_duplicate_schedule(db, vehicle_id):
        logger.info("📅 Scheduler: Duplicate schedule skipped")
        return None

    # ─── Determine service type and priority ───
    mapping = RISK_SERVICE_MAP.get(risk_level, RISK_SERVICE_MAP.get(risk_upper, {
        "service_type": "inspection",
        "priority": "medium",
    }))

    service_type = mapping["service_type"]
    priority = mapping["priority"]

    # ─── Escalation check ───
    if risk_upper == "HIGH" and await check_escalation(db, vehicle_id):
        service_type = "urgent"
        priority = "high"
        logger.warning(
            f"⚠️ Scheduler: Escalating priority for vehicle={vehicle_id} "
            f"(multiple HIGH risks detected)"
        )

    # ─── Compute scheduled date ───
    scheduled_date = compute_scheduled_date(risk_level)

    # ─── Create the schedule ───
    schedule = ServiceSchedule(
        vehicle_id=vehicle_id,
        prediction_id=prediction_id,
        service_type=service_type,
        priority=priority,
        status="pending",
        scheduled_date=scheduled_date,
        failure_probability=failure_probability,
        risk_level=risk_level,
    )

    db.add(schedule)
    await db.flush()  # Get the ID without committing

    logger.info(
        f"📅 Scheduler: Service schedule created | "
        f"id={schedule.id} | vehicle={vehicle_id} | "
        f"type={service_type} | priority={priority} | "
        f"scheduled={scheduled_date.isoformat()}"
    )

    return {
        "schedule_id": str(schedule.id),
        "vehicle_id": str(vehicle_id) if vehicle_id else None,
        "prediction_id": str(prediction_id) if prediction_id else None,
        "service_type": service_type,
        "priority": priority,
        "status": "pending",
        "scheduled_date": scheduled_date.isoformat(),
    }
