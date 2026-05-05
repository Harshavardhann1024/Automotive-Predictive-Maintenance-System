import os
import smtplib
import logging
from email.message import EmailMessage
from typing import Optional

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, message: str) -> bool:
    """
    Sends an email using SMTP (Gmail).
    Expects EMAIL_USER and EMAIL_PASS environment variables.
    """
    email_user = os.environ.get("EMAIL_USER")
    email_pass = os.environ.get("EMAIL_PASS")

    if not email_user or not email_pass:
        logger.warning("EMAIL_USER or EMAIL_PASS not set. Skipping email send.")
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = to_email
    
    # We set the content as HTML
    msg.add_alternative(message, subtype='html')

    try:
        # Use a background task / thread in production, or async SMTP library like aiosmtplib.
        # Since standard smtplib is synchronous, we run it directly here, but it's meant to be
        # called via FastAPI BackgroundTasks so it won't block the API response.
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_user, email_pass)
            smtp.send_message(msg)
        logger.info(f"Email sent to {to_email} with subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
