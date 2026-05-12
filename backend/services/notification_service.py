import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from backend.core.config import settings
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.email_service import send_email as send_email_via_smtp

class NotificationService:
    SECRET_KEY = settings.SECRET_KEY
    
    @staticmethod
    def generate_decision_token(prediction_id: str, vehicle_id: str, user_id: str, action: str, expires_in_hours: int = 48) -> str:
        """
        Generate a secure JWT token for a specific action.
        """
        expiration = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
        payload = {
            "prediction_id": str(prediction_id),
            "vehicle_id": str(vehicle_id),
            "user_id": str(user_id),
            "action": action, # APPROVE_SERVICE, REMIND_LATER, IGNORE_ALERT
            "exp": expiration
        }
        return jwt.encode(payload, NotificationService.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_decision_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify the token and extract payload.
        Returns payload if valid, None if invalid or expired.
        """
        try:
            payload = jwt.decode(token, NotificationService.SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.PyJWTError as e:
            print(f"Invalid token: {e}")
            return None

    @staticmethod
    def generate_email_content(
        user_name: str, 
        vehicle_model: str, 
        risk_level: str, 
        probability: float, 
        rul: int,
        prediction_id: str,
        vehicle_id: str,
        user_id: str,
        base_url: str = "http://localhost:8000"
    ) -> str:
        # Generate tokens for actions
        approve_token = NotificationService.generate_decision_token(prediction_id, vehicle_id, user_id, "APPROVE_SERVICE")
        remind_token = NotificationService.generate_decision_token(prediction_id, vehicle_id, user_id, "REMIND_LATER")
        ignore_token = NotificationService.generate_decision_token(prediction_id, vehicle_id, user_id, "IGNORE_ALERT")
        
        # Build action links
        approve_link = f"{base_url}/notifications/response?token={approve_token}"
        remind_link = f"{base_url}/notifications/response?token={remind_token}"
        ignore_link = f"{base_url}/notifications/response?token={ignore_token}"
        
        # We will use an HTML template loaded from file
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "email_notification.html")
        try:
            with open(template_path, "r") as file:
                html_content = file.read()
        except FileNotFoundError:
            # Fallback if template doesn't exist yet
            return f"""
            <h2>Risk Detected: {risk_level}</h2>
            <p>Approve: <a href="{approve_link}">Click Here</a></p>
            """
            
        # Replace placeholders
        html_content = html_content.replace("{{USER_NAME}}", user_name)
        html_content = html_content.replace("{{VEHICLE_MODEL}}", vehicle_model)
        html_content = html_content.replace("{{RISK_LEVEL}}", risk_level.upper())
        html_content = html_content.replace("{{RISK_LEVEL_LOWER}}", risk_level.lower())
        html_content = html_content.replace("{{PROBABILITY}}", f"{probability * 100:.1f}%")
        html_content = html_content.replace("{{RUL}}", str(rul))
        
        html_content = html_content.replace("{{APPROVE_LINK}}", approve_link)
        html_content = html_content.replace("{{REMIND_LINK}}", remind_link)
        html_content = html_content.replace("{{IGNORE_LINK}}", ignore_link)
        
        return html_content
        
    @staticmethod
    async def create_notification(
        title: str,
        message: str,
        priority: str,
        background_tasks: BackgroundTasks,
        user_email: Optional[str] = None,
        user_id: Optional[str] = None,
        db_session: Optional[AsyncSession] = None,
        prediction_id: Optional[str] = None,
        vehicle_id: Optional[str] = None,
        probability: Optional[float] = None,
        rul: Optional[int] = 30
    ):
        """
        Bridges the core system with the notification logic.
        Sends email based on priority and template.
        """
        if not user_email:
            print(f"Skipping notification for {title} - no user email.")
            return

        # Maintenance Alert Logic
        if priority.lower() in ["high", "critical", "medium"] or "risk" in title.lower():
            # If we don't have all IDs, we try to extract from context or use fallbacks
            # In a real flow, these would be passed from Notifier
            
            html_content = NotificationService.generate_email_content(
                user_name="Vehicle Owner",
                vehicle_model="Your Vehicle",
                risk_level=priority,
                probability=probability or 0.88,
                rul=rul or 14,
                prediction_id=prediction_id or "00000000-0000-0000-0000-000000000000",
                vehicle_id=vehicle_id or "00000000-0000-0000-0000-000000000000",
                user_id=user_id or "00000000-0000-0000-0000-000000000000"
            )
            
            background_tasks.add_task(
                send_email_via_smtp,
                user_email,
                f"Maintenance Alert: {title}",
                html_content
            )
        else:
            # Regular notification (plain text/simple HTML)
            background_tasks.add_task(
                send_email_via_smtp,
                user_email,
                title,
                f"<p>{message}</p>"
            )

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str):
        """Mock for testing purposes if needed."""
        print(f"--- MOCK EMAIL SEND TO {to_email} ---")
        print(f"Subject: {subject}")
        print("--- END MOCK EMAIL ---")
        return True
