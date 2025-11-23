"""
Email sending utilities (stub implementation).
This demonstrates how to structure email sending.
In production, you'd use a real SMTP server or service like SendGrid.
"""
import logging
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_alert_email(to_emails: List[str], subject: str, body: str) -> bool:
    """
    Send an alert email (stub implementation).
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject
        body: Email body (plain text)
    
    Returns:
        True if email was "sent" successfully
    
    To enable real email sending:
    1. Set SMTP_* environment variables in .env
    2. Uncomment the SMTP code below
    3. Install required package if using specific service (e.g., sendgrid)
    
    Example with SMTP:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM
        msg['To'] = ', '.join(to_emails)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    """
    # Stub: Just log the email instead of sending
    logger.info(f"[EMAIL STUB] Would send email to {to_emails}")
    logger.info(f"[EMAIL STUB] Subject: {subject}")
    logger.info(f"[EMAIL STUB] Body: {body}")
    
    # In production, implement real email sending here
    # For now, we simulate success
    return True
