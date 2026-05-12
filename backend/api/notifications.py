from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any
import datetime

from backend.core.database import get_db
from backend.services.notification_service import NotificationService
# from backend.models.service_request import ServiceRequest # Potentially remove or refactor
from backend.models.service_schedule import ServiceSchedule

router = APIRouter(prefix="/notifications", tags=["Notifications"])

async def process_downstream_action(db: AsyncSession, request_id: str, action: str):
    """
    Background task to handle downstream workflow based on user decision.
    This function should operate on ServiceSchedule directly.
    """
    # Assuming request_id here refers to ServiceSchedule.id or a linked entity
    # For now, let's assume it's the prediction_id that links to ServiceSchedule
    result = await db.execute(select(ServiceSchedule).where(ServiceSchedule.prediction_id == request_id))
    schedule = result.scalars().first()
    if not schedule:
        return

    if action == "APPROVE_SERVICE":
        schedule.status = "scheduled"
    elif action == "REMIND_LATER":
        schedule.status = "pending" # Or a new status like "deferred"
    elif action == "IGNORE_ALERT":
        schedule.status = "cancelled"
    
    await db.commit()

@router.get("/response")
async def handle_notification_response(
    token: str = Query(..., description="JWT action token from email"),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Any:
    """
    Callback endpoint for email action links.
    Validates the token, records the decision, and triggers downstream actions.
    """
    payload = NotificationService.verify_decision_token(token)
    
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    prediction_id = payload.get("prediction_id")
    vehicle_id = payload.get("vehicle_id")
    action = payload.get("action")
    
    if not prediction_id or not action:
        raise HTTPException(status_code=400, detail="Malformed token payload")
        
    # Find the associated service schedule
    result = await db.execute(select(ServiceSchedule).where(ServiceSchedule.prediction_id == prediction_id))
    db_schedule = result.scalars().first()
    
    # If no service schedule exists yet (e.g., for a MEDIUM risk alert that only notified)
    if not db_schedule:
        # This scenario implies a MEDIUM risk alert was sent, and now the user wants to schedule.
        # We need to retrieve the original risk level and probability from the prediction
        # or ensure it's part of the token payload. For now, using a placeholder.
        # Ideally, the token should contain enough info to reconstruct the schedule.
        # For this example, let's assume the token has 'risk_level' and 'failure_probability'
        # or we fetch it from the prediction table if available.
        # For simplicity, let's assume the token has 'risk_level' and 'failure_probability'
        # or we fetch it from the prediction table if available.
        # For now, we'll use a placeholder and a default scheduled_date.
        db_schedule = ServiceSchedule(
            vehicle_id=vehicle_id,
            prediction_id=prediction_id,
            risk_level=payload.get("risk_level", "Medium"), # Get from token or prediction
            failure_probability=payload.get("probability", 0.5), # Get from token or prediction
            service_type="inspection", # Default for user-initiated schedule
            priority="medium",
            status="pending",
            scheduled_date=datetime.datetime.utcnow() + datetime.timedelta(days=3) # Default
        )
        db.add(db_schedule)
        await db.commit()
        await db.refresh(db_schedule)
        
    # Idempotency check: if user already made a decision, we don't overwrite it
    # This logic needs to be adapted for ServiceSchedule.
    # We might need a new field on ServiceSchedule like 'last_user_decision'
    if db_schedule.status == "scheduled" and action == "APPROVE_SERVICE":
        return {"status": "success", "message": f"Action {action} was already recorded."}

    # Record the user decision
    # Update status based on decision
    if action == "APPROVE_SERVICE":
        db_schedule.status = "scheduled"
        message = "Service successfully scheduled. Thank you for taking action."
    elif action == "REMIND_LATER":
        db_schedule.status = "pending" # Or a new status like "deferred"
        message = "We will remind you later about this alert."
    elif action == "IGNORE_ALERT":
        db_schedule.status = "cancelled"
        message = "Alert ignored. Note that this may increase the risk of failure."
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
        
    await db.commit()
    
    # Trigger downstream tasks, passing prediction_id to link to the schedule
    background_tasks.add_task(process_downstream_action, db, prediction_id, action)
    
    return {
        "status": "success",
        "action": action,
        "message": message
    }

@router.post("/test_email")
async def test_email_notification(
    background_tasks: BackgroundTasks,
    email: str = Query(..., description="Email address to send the test alert to"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Test endpoint to directly trigger the HTML email notification.
    """
    await NotificationService.create_notification(
        title="High Risk Detected",
        message="Test alert",
        priority="high",
        background_tasks=background_tasks,
        user_email=email,
        user_id="test_user",
        db_session=db,
        prediction_id="11111111-1111-1111-1111-111111111111",
        vehicle_id="22222222-2222-2222-2222-222222222222",
        probability=0.95,
        rul=7
    )
    return {"status": "success", "message": f"Test email dispatched to {email}"}
