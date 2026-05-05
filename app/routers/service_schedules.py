"""
Service Schedules Router — CRUD + dashboard endpoints for service scheduling.
==============================================================================
GET    /service-schedules/            → List all schedules (with filters)
GET    /service-schedules/stats       → Dashboard summary statistics
GET    /service-schedules/{vehicle_id}/vehicle → Schedules by vehicle
GET    /service-schedules/{id}        → Single schedule by ID
PATCH  /service-schedules/{id}        → Update schedule (status, reschedule, assign)
DELETE /service-schedules/{id}        → Cancel a schedule
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.service_schedule import ServiceSchedule
from app.schemas.service_schedule import (
    ServiceScheduleResponse,
    ServiceScheduleUpdate,
    ServiceScheduleStats,
)
from app.services.service_scheduler import check_and_notify_overdue_services

logger = logging.getLogger("routers.service_schedules")

router = APIRouter()


@router.get("/", response_model=List[ServiceScheduleResponse])
async def get_all_schedules(
    status: Optional[str] = Query(None, description="Filter by status: pending|scheduled|in_progress|completed|cancelled"),
    priority: Optional[str] = Query(None, description="Filter by priority: low|medium|high"),
    service_type: Optional[str] = Query(None, description="Filter by type: inspection|repair|urgent"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Get all service schedules with optional filters."""
    try:
        query = select(ServiceSchedule)

        if status:
            query = query.where(ServiceSchedule.status == status)
        if priority:
            query = query.where(ServiceSchedule.priority == priority)
        if service_type:
            query = query.where(ServiceSchedule.service_type == service_type)

        query = query.order_by(desc(ServiceSchedule.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        schedules = result.scalars().all()

        return [ServiceScheduleResponse.model_validate(s) for s in schedules]
    except Exception as e:
        logger.exception("Failed to fetch service schedules")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-overdue-checks")
async def trigger_overdue_checks(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Check for overdue services and trigger escalation notifications (including emails).
    Intended to be called periodically via cron or external scheduler.
    """
    try:
        count = await check_and_notify_overdue_services(db, background_tasks)
        return {"message": "Overdue check completed", "notified_count": count}
    except Exception as e:
        logger.exception("Failed to check overdue services")
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/stats", response_model=ServiceScheduleStats)
async def get_schedule_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard summary statistics for service schedules."""
    try:
        now = datetime.utcnow()
        next_24h = now + timedelta(hours=24)

        # Total
        total_q = select(func.count(ServiceSchedule.id))
        total_result = await db.execute(total_q)
        total = total_result.scalar() or 0

        # Status counts
        status_counts = {}
        for s in ["pending", "scheduled", "in_progress", "completed", "cancelled"]:
            q = select(func.count(ServiceSchedule.id)).where(ServiceSchedule.status == s)
            r = await db.execute(q)
            status_counts[s] = r.scalar() or 0

        # Priority counts
        priority_counts = {}
        for p in ["high", "medium", "low"]:
            q = select(func.count(ServiceSchedule.id)).where(
                and_(
                    ServiceSchedule.priority == p,
                    ServiceSchedule.status.in_(["pending", "scheduled", "in_progress"]),
                )
            )
            r = await db.execute(q)
            priority_counts[p] = r.scalar() or 0

        # Upcoming 24h
        upcoming_q = select(func.count(ServiceSchedule.id)).where(
            and_(
                ServiceSchedule.scheduled_date >= now,
                ServiceSchedule.scheduled_date <= next_24h,
                ServiceSchedule.status.in_(["pending", "scheduled"]),
            )
        )
        upcoming_result = await db.execute(upcoming_q)
        upcoming = upcoming_result.scalar() or 0

        # Overdue
        overdue_q = select(func.count(ServiceSchedule.id)).where(
            and_(
                ServiceSchedule.scheduled_date < now,
                ServiceSchedule.status.in_(["pending", "scheduled"]),
            )
        )
        overdue_result = await db.execute(overdue_q)
        overdue = overdue_result.scalar() or 0

        # Service type counts (active only)
        type_counts = {}
        for t in ["urgent", "inspection", "repair"]:
            q = select(func.count(ServiceSchedule.id)).where(
                and_(
                    ServiceSchedule.service_type == t,
                    ServiceSchedule.status.in_(["pending", "scheduled", "in_progress"]),
                )
            )
            r = await db.execute(q)
            type_counts[t] = r.scalar() or 0

        return ServiceScheduleStats(
            total_schedules=total,
            pending_count=status_counts.get("pending", 0),
            scheduled_count=status_counts.get("scheduled", 0),
            in_progress_count=status_counts.get("in_progress", 0),
            completed_count=status_counts.get("completed", 0),
            cancelled_count=status_counts.get("cancelled", 0),
            high_priority_count=priority_counts.get("high", 0),
            medium_priority_count=priority_counts.get("medium", 0),
            low_priority_count=priority_counts.get("low", 0),
            upcoming_24h=upcoming,
            overdue_count=overdue,
            urgent_services=type_counts.get("urgent", 0),
            inspection_services=type_counts.get("inspection", 0),
            repair_services=type_counts.get("repair", 0),
        )
    except Exception as e:
        logger.exception("Failed to compute schedule stats")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{schedule_id}", response_model=ServiceScheduleResponse)
async def get_schedule_by_id(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single service schedule by ID."""
    try:
        query = select(ServiceSchedule).where(ServiceSchedule.id == schedule_id)
        result = await db.execute(query)
        schedule = result.scalar_one_or_none()

        if not schedule:
            raise HTTPException(status_code=404, detail="Service schedule not found")

        return ServiceScheduleResponse.model_validate(schedule)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vehicle/{vehicle_id}", response_model=List[ServiceScheduleResponse])
async def get_schedules_by_vehicle(
    vehicle_id: UUID,
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get service schedules for a specific vehicle."""
    try:
        query = select(ServiceSchedule).where(ServiceSchedule.vehicle_id == vehicle_id)

        if status:
            query = query.where(ServiceSchedule.status == status)

        query = query.order_by(desc(ServiceSchedule.scheduled_date)).limit(limit)
        result = await db.execute(query)
        schedules = result.scalars().all()

        return [ServiceScheduleResponse.model_validate(s) for s in schedules]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{schedule_id}", response_model=ServiceScheduleResponse)
async def update_schedule(
    schedule_id: UUID,
    update_data: ServiceScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a service schedule (status, reschedule, assign technician).
    Supports partial updates — only provided fields are changed.
    """
    try:
        query = select(ServiceSchedule).where(ServiceSchedule.id == schedule_id)
        result = await db.execute(query)
        schedule = result.scalar_one_or_none()

        if not schedule:
            raise HTTPException(status_code=404, detail="Service schedule not found")

        # Apply partial updates
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(schedule, field, value)

        schedule.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(schedule)

        logger.info(
            f"📅 Schedule updated | id={schedule_id} | changes={list(update_dict.keys())}"
        )

        return ServiceScheduleResponse.model_validate(schedule)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{schedule_id}")
async def cancel_schedule(
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Cancel a service schedule (soft delete — sets status to cancelled)."""
    try:
        query = select(ServiceSchedule).where(ServiceSchedule.id == schedule_id)
        result = await db.execute(query)
        schedule = result.scalar_one_or_none()

        if not schedule:
            raise HTTPException(status_code=404, detail="Service schedule not found")

        schedule.status = "cancelled"
        schedule.updated_at = datetime.utcnow()
        await db.commit()

        logger.info(f"📅 Schedule cancelled | id={schedule_id}")

        return {"message": "Schedule cancelled", "id": str(schedule_id)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
