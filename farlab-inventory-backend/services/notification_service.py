# services/notification_service.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from models.part import Part
from utils.logging_config import get_logger
from utils.config import settings

# Get a logger for this module
logger = get_logger(__name__)


def _send_email(to_email: str, subject: str, body_html: str):
    """"
    Handles the connection to the SMTP server and sends the email.
    This is a private helper function for this module.
    """
    # Ensure all required environment variables are set
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SENDER_EMAIL]):
        logger.error(
            "SMTP environment variables not configured. Cannot send email.")
        return

    try:
        # Create the email message object
        msg = MIMEMultipart()
        msg["From"] = settings.SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        # Connect to the SMTP server and send the email
        # The with statement ensure automatic connection close
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            logger.info("Email sent successfully to %s", to_email)

    except Exception as e:
        logger.error("Failed to send email to %s. Reason: %s",
                     to_email, e, exc_info=True)


def send_low_stock_email_notification(part: Part, admin_email: str):
    """"
    Sends an email notification for low stock.
    """
    subject = f"Lows Stock Alert: {part.name}"

    body = f"""
    <p> This is an automated alert to inform you that a part in the inventory is running low on stock.</p>

    <h2>Part Details:</h2>
    <ul>
        <li><strong>Part Name:</strong>{part.name}</li>
        <li><strong>Part Number:</strong>{part.part_number}</li>
        <li><strong>Current Quantity:</strong>{part.quantity_in_stock}</li>
        <li><strong>Minimum Stock Level:</strong>{part.minimum_stock_level}</li>
    </ul>
"""

    # Send email to the admin
    logger.info("Sending low stock notification for '%s' to '%s' and '%s'",
                part.name, admin_email)

    _send_email(admin_email, subject, body)


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
