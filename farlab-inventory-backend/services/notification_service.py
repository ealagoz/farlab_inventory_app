# services/notification_service.py
import smtplib
import html
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict
from datetime import datetime, timedelta
import time 
import re 
from dataclasses import dataclass

from models.part import Part
from utils.logging_config import get_logger
from utils.config import settings

# Get a logger for this module
logger = get_logger(__name__)


@dataclass
class EmailRateLimit:
    """Track email sending rate limits."""
    last_sent: Dict[str, datetime] = None
    send_count: Dict[str, int] = None

    def __post_init__(self):
        if self.last_sent is None:
            self.last_sent = {}
        if self.send_count is None:
            self.send_count = {}

# Global rate limiter (use Redis in production?)
email_limiter = EmailRateLimit()

def esccape_html_content(content: str) -> str:
    """Safely escape HTML content to prevent injection."""
    if not content:
        return ""
    return html.escape(str(content))

def check_email_rate_limit(email_key: str, max_per_hour: int = 10) -> bool:
    """Check if email sending is within rate limits."""
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)

    # Reset counter if hour passed
    if email_key not in email_limiter.last_sent or email_limiter.last_sent[email_key] < hour_ago:
        email_limiter.send_count[email_key] = 0
    
    # Check if under limit
    current_count = email_limiter.send_count.get(email_key, 0)
    if current_count >= max_per_hour:
        logger.warning("Email rate limit exceeded for key: %s", email_key)
        return False
    
    # Update counters
    email_limiter.last_sent[email_key] = now 
    email_limiter.send_count[email_key] = current_count + 1



def _send_email(to_email: str, subject: str, body_html: str):
    """"
    Handles the connection to the SMTP server and sends the email.
    This is a private helper function for this module.
    """
    # Validate email address format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[a-zA-Z]{2,}$'
    if not re.match(email_pattern, to_email):
        raise ValueError(f"Invalid email address: {to_email}")

    # Ensure all required environment variables are set
    missing_settings = []
    required_settings = {
        "SMTP_HOST": settings.SMTP_HOST,
        "SMTP_PORT": settings.SMTP_PORT,
        "SMTP_USER": settings.SMTP_USER,
        "SMTP_PASSWORD": settings.SMTP_PASSWORD,
        "SENDER_EMAIL": settings.SENDER_EMAIL
    }
    for name, value in required_settings.items():
        if not value:
            missing_settings.append(name)
    
    if missing_settings:
        raise ValueError(f"Missing SMTP configuration: {', '.join(missing_settings)}")

    try:
        # Create the email message object
        msg = MIMEMultipart()
        msg["From"] = settings.SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid()

        msg.attach(MIMEText(body_html, "html"))

        # Connect to the SMTP server and send the email
        # The with statement ensure automatic connection close
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info("Email sent successfully to %s", to_email)

    except Exception as e:
        logger.error("Failed to send email to %s. Reason: %s",
                     to_email, e, exc_info=True)
        raise 


def send_low_stock_email_notification(part: Part, admin_email: str):
    """"
    Sends an email notification for low stock with security and rate limiting.
    """
    # Rate limiting check
    rate_key = f"low_stock_{part.id}"
    if not check_email_rate_limit(rate_key, max_per_hour=5):
        logger.warning("Rate limit hit for part %s notifications", part.name)
        return
    
    # Safely escape all dynamic content
    safe_name = esccape_html_content(part.name)
    safe_part_number = esccape_html_content(part.part_number)
    safe_quantity = esccape_html_content(str(part.quantity_in_stock))
    safe_minimum = esccape_html_content(str(part.minimum_stock_level))

    # Notification email subject
    subject = f"Lows Stock Alert: {part.name}"

    # Safe notification email with escaped content
    body = f"""
    <p> This is an automated alert to inform you that a part in the inventory is running low on stock.</p>

    <h2>Part Details:</h2>
    <ul>
        <li><strong>Part Name:</strong>{safe_name}</li>
        <li><strong>Part Number:</strong>{safe_part_number}</li>
        <li><strong>Current Quantity:</strong>{safe_quantity}</li>
        <li><strong>Minimum Stock Level:</strong>{safe_minimum}</li>
    </ul>
    <p><small>This is an automated message from FARLAB Inventory System at {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}</small></p>
"""

    # Send email to the admin
    logger.info("Sending low stock notification for '%s' to '%s' and '%s'",
                part.name, admin_email)

    # _send_email(admin_email, subject, body)
    # Send with retry logic
    send_email_with_retry(admin_email, subject, body)

def send_email_with_retry(to_email: str, subject: str, body: str, max_retries: int = 3):
    """Send email with retry logic and better error handling."""
    for attempt in range(max_retries):
        try:
            _send_email(to_email, subject, body)
            return  # Success
        except smtplib.SMTPAuthenticationError as e:
            logger.error("SMTP authentication failed: %s", e)
            break  # Don't retry auth failures
        except smtplib.SMTPServerDisconnected as e:
            if attempt == max_retries - 1:
                logger.error("SMTP server disconnected after %d attempts: %s", max_retries, e)
                raise
            logger.warning("SMTP disconnected, retrying attempt %d: %s", attempt + 1, e)
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error("Email sending failed after %d attempts: %s", max_retries, e)
                raise
            logger.warning("Email attempt %d failed, retrying: %s", attempt + 1, e)
            time.sleep(2 ** attempt)


def send_periodic_alert_summary(alerts: List[Part], admin_email: str):
    """"
    Sends a summary email of all parts that are currently low on stock.
    This is the function for the scheduled task.
    """
    if not alerts:
        logger.info("Scheduler: No active alerts to send in the summary email.")
        return

    subject = "Daily Inventory Alert Summary"

    # Create an html list of the parts that are low in stock
    parts_list_html = "".join([
        f"<li><strong>{part.name}</strong> (Part #{part.part_number}) - "
        f"In Stock: {part.quantity_in_stock}, "
        f"Minimum Threshold: {part.minimum_stock_level}</li>"
        for part in alerts
    ])

    body = f"""
        <p>This is your daily summary of inventory items that are low on stock.</p>
        <h2>Active Low Stock Alerts:</h2>
        <ul>
            {parts_list_html}
        </ul>
        <p>Please review the inventory and take the necessary action.</p>
        """

    _send_email(admin_email, subject, body)
