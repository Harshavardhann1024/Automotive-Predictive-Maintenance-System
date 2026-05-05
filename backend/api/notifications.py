from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any
import datetime

from backend.core.database import get_db
from backend.services.notification_service import NotificationService
from backend.models.service_request import ServiceRequest
from backend.models.service_schedule import ServiceSchedule

router = APIRouter(prefix="/notifications", tags=["Notifications"])

async def process_downstream_action(db: AsyncSession, request_id: str, action: str):
    """
    Background task to handle downstream workflow based on user decision.
    """
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.id == request_id))
    db_request = result.scalars().first()
    if not db_request:
        return

    # Update ServiceSchedule status if it exists for this prediction
    if db_request.prediction_id:
        schedule_result = await db.execute(select(ServiceSchedule).where(ServiceSchedule.prediction_id == db_request.prediction_id))
        schedule = schedule_result.scalars().first()
        if schedule:
            if action == "APPROVE_SERVICE":
                schedule.status = "scheduled"
            elif action == "REMIND_LATER":
                schedule.status = "pending"
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
        
    # Find the associated service request
    result = await db.execute(select(ServiceRequest).where(ServiceRequest.prediction_id == prediction_id))
    db_request = result.scalars().first()
    
    # If no service request exists yet, we create one (e.g. for medium risk alerts)
    if not db_request:
        db_request = ServiceRequest(
            vehicle_id=vehicle_id,
            prediction_id=prediction_id,
            risk_level="UNKNOWN", # Should be populated from prediction if available
            status="PENDING"
        )
        db.add(db_request)
        await db.commit()
        await db.refresh(db_request)
        
    # Idempotency check: if user already made a decision, we don't overwrite it
    if db_request.user_decision is not None and db_request.user_decision == action:
        return {"status": "success", "message": f"Action {action} was already recorded."}

    # Record the user decision
    db_request.user_decision = action
    db_request.decision_timestamp = datetime.datetime.utcnow()
    
    # Update status based on decision
    if action == "APPROVE_SERVICE":
        db_request.status = "SCHEDULED"
        if not db_request.scheduled_time:
            db_request.scheduled_time = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        message = "Service successfully scheduled. Thank you for taking action."
    elif action == "REMIND_LATER":
        db_request.status = "DEFERRED"
        message = "We will remind you later about this alert."
    elif action == "IGNORE_ALERT":
        db_request.status = "CANCELLED"
        message = "Alert ignored. Note that this may increase the risk of failure."
    else:
        raise HTTPException(status_code=400, detail="Unknown action")
        
    await db.commit()
    
    # Trigger downstream tasks
    background_tasks.add_task(process_downstream_action, db, db_request.id, action)
    
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

