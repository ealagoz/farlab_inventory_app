# services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from services.notification_service import send_periodic_alert_summary
from services.alert_service import get_low_stock_parts
from utils.logging_config import get_logger
from utils.config import settings

# Get a logger for this module
logger = get_logger(__name__)


def scheduled_alert_job():
    """"
    The actual job to be run by the scheduler.
    It creates its own database session to ensure it's thread-safe.
    """
    logger.info("Running scheduled job to check for low stock alerts...")

    db: Session = SessionLocal()  # Create a new db session for this job

    try:
        # 1. Fetch all currently low on stock parts from db
        low_stock_parts = get_low_stock_parts(db)

        # 2. Send the summary email if there are any alerts
        if low_stock_parts:
            logger.info(
                "Found '%d' low-stock parts. Sending summary email.", len(low_stock_parts))
            send_periodic_alert_summary(low_stock_parts, settings.ADMIN_EMAIL)
        else:
            logger.info("No low stock parts found. No summary email needed.")
    except Exception as e:
        logger.error("Error in scheduled alert job: %s", e, exc_info=True)
    finally:
        db.close()  # Ensure db is closed after the job


def start_scheduler():
    """"
    Initializes and starts the background scheduler.
    """
    scheduler = BackgroundScheduler(daemon=True)

    # Schedule the job to run every day at 9:00 AM
    # The 'cron' trigger is powerful for setting specific times.
    # scheduler.add_job(scheduled_alert_job, 'cron', hour=9, minute=0)

    # For testing purposes, one can uncomment the line below
    # This will run the job every 10 minute default, which is useful for development
    scheduler.add_job(scheduled_alert_job, 'interval',
                      minutes=settings.SCHEDULER_INTERVAL_MINUTES)

    scheduler.start()
    logger.info(
        "Background scheduler started. Periodic email alerts are active.")
