"""
Scheduler — Service Request Management
========================================
Internal service within the Action Agent (NOT a separate agent).
Handles creating and managing service_requests records in the database.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.service_request import ServiceRequest

logger = logging.getLogger("agents.action.scheduler")

# ─── Scheduling configuration ───
DEFAULT_SLOT_DURATION_HOURS = 2
BUSINESS_START_HOUR = 8   # 08:00 AM
BUSINESS_END_HOUR = 18    # 06:00 PM
MAX_SLOTS_PER_DAY = 5     # Maximum concurrent service slots


class Scheduler:
    """
    Manages service request creation and slot assignment.
    Finds the earliest available service slot and persists the request.
    """

    @staticmethod
    async def schedule_service(
        db: AsyncSession,
        vehicle_id: Optional[UUID],
        risk_level: str,
    ) -> Dict[str, Any]:
        """
        Create a service request and assign the earliest available slot.

        Parameters
        ----------
        db : AsyncSession
            Database session
        vehicle_id : UUID or None
            The vehicle to schedule service for
        risk_level : str
            Risk level that triggered the scheduling

        Returns
        -------
        dict with:
            service_request_id : str (UUID)
            scheduled_time     : str (ISO format)
            status             : str
        """
        scheduled_time = await Scheduler._find_next_slot(db)

        service_request = ServiceRequest(
            vehicle_id=vehicle_id,
            risk_level=risk_level,
            scheduled_time=scheduled_time,
            status="SCHEDULED",
        )

        db.add(service_request)
        await db.flush()  # Get the ID without committing (caller manages transaction)

        logger.info(
            f"📅 Scheduler: Service request created | "
            f"id={service_request.id} | vehicle={vehicle_id} | "
            f"risk={risk_level} | slot={scheduled_time.isoformat()}"
        )

        return {
            "service_request_id": str(service_request.id),
            "scheduled_time": scheduled_time.isoformat(),
            "status": "SCHEDULED",
        }

    @staticmethod
    async def _find_next_slot(db: AsyncSession) -> datetime:
        """
        Find the earliest available service slot.

        Logic:
        - Start from the next business hour boundary
        - Check each slot for capacity (max slots per day)
        - Skip non-business hours and full days
        """
        now = datetime.utcnow()
        candidate = Scheduler._next_business_hour(now)

        # Look up to 14 days ahead for an available slot
        for _ in range(14 * MAX_SLOTS_PER_DAY):
            # Count existing requests in the same time window
            window_start = candidate.replace(minute=0, second=0, microsecond=0)
            window_end = window_start + timedelta(hours=DEFAULT_SLOT_DURATION_HOURS)

            count_query = select(func.count(ServiceRequest.id)).where(
                ServiceRequest.scheduled_time >= window_start,
                ServiceRequest.scheduled_time < window_end,
                ServiceRequest.status != "CANCELLED",
            )
            result = await db.execute(count_query)
            slot_count = result.scalar() or 0

            if slot_count < MAX_SLOTS_PER_DAY:
                return candidate

            # Move to next slot
            candidate += timedelta(hours=DEFAULT_SLOT_DURATION_HOURS)
            candidate = Scheduler._next_business_hour(candidate)

        # Fallback: schedule 24h from now if no slots found
        logger.warning("⚠️ Scheduler: No available slots found in 14-day window. Using fallback.")
        return now + timedelta(hours=24)

    @staticmethod
    def _next_business_hour(dt: datetime) -> datetime:
        """
        Advance the datetime to the next valid business hour.
        Skips weekends and non-business hours.
        """
        # Round up to next hour
        if dt.minute > 0 or dt.second > 0:
            dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

        # Skip to business hours
        if dt.hour >= BUSINESS_END_HOUR:
            dt = dt.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)
            dt += timedelta(days=1)

        if dt.hour < BUSINESS_START_HOUR:
            dt = dt.replace(hour=BUSINESS_START_HOUR, minute=0, second=0, microsecond=0)

        # Skip weekends (Saturday=5, Sunday=6)
        while dt.weekday() in (5, 6):
            dt += timedelta(days=1)

        return dt
