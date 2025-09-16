# services/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import get_background_db_session
from services.notification_service import send_periodic_alert_summary
from services.alert_service import get_low_stock_parts
from utils.logging_config import get_logger
from utils.config import settings

import atexit
import time 
from datetime import datetime
from threading import Event

# Global scheduler instance for proper shutdown
scheduler_instance = None
shutdown_event = Event()

# Get a logger for this module
logger = get_logger(__name__)


def scheduled_alert_job():
    """"
    The actual job to be run by the scheduler.
    It creates its own database session to ensure it's thread-safe.
    """
    logger.info("Running scheduled job to check for low stock alerts...")

    # Use the background database session context manager
    with get_background_db_session() as db:
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


def start_scheduler():
    """"
    Initializes and starts the background scheduler with proper lifecycle.
    """
    global scheduler_instance

    # scheduler = BackgroundScheduler(daemon=True)
    scheduler_instance = BackgroundScheduler(
        daemon=False, # Allow proper cleanup
        job_defaults={
            'coalesce': True, # Prevent job pile-up
            'max_instances': 1, # Only one instance at a time
            'misfire_grace_time': 300 # 5-minute grace period
        }
    )

    # Schedule the job to run every day at 9:00 AM
    # The 'cron' trigger is powerful for setting specific times.
    # scheduler.add_job(scheduled_alert_job, 'cron', hour=9, minute=0)

    # For testing purposes, one can uncomment the line below
    # This will run the job every 60 minute default, which is useful for development
    scheduler_instance.add_job(
        func=scheduled_alert_job, # Wrapped with error handling
        trigger='interval',
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        id="alert_summary_job", # Give job an ID for monitoring
        replace_existing=True # Handle restarts gracefully
    )

    scheduler_instance.start()

    # Register cleanup function
    atexit.register(shutdown_scheduler)
    logger.info(
        "Background scheduler started safely with job ID: alert_summary_job")

def shutdown_scheduler():
    """Gracefully shutdown the scheduler."""
    global scheduler_instance
    if scheduler_instance and scheduler_instance.running:
        logger.info("Shutting down scheduler ...")
        scheduler_instance.shutdown(wait=True) # Wait for current job to finish
        logger.info("Scheduler shut down gracefully")

def safe_scheduler_alert_job():
    """Enhanced job wrapper with better error handling."""
    job_start_time = time.time()
    logger.info("Starting scheduled alert job at %s", datetime.now())

    try: 
        # Use the background database session context manager
        with get_background_db_session() as db:
            # Check if we should run (avoid duplicate notifications)
            if should_send_daily_summary(db):
                low_stock_parts = get_low_stock_parts(db)

                if low_stock_parts:
                    logger.info("Found %d low-stock parts. Sending summary email.", len(low_stock_parts))

                    # Send notification with retry logic
                    send_with_retry(
                        send_periodic_alert_summary,
                        low_stock_parts,
                        settings.ADMIN_EMAIL,
                        max_retries=3
                    )

                    # Mark summary as sent
                    mark_summary_sent(db)
                else:
                    logger.info("No low stock parts found.")
            else:
                logger.info("Daily summary already sent today, skipping.")
    
    except Exception as e:
        logger.error("Critical error in scheduled job: %s", e, exc_info=True)
        # TODO: Send alert about scheduler failure
    
    finally:
        job_duration = time.time() - job_start_time
        logger.info("Scheduled job completed in %.2f seconds", job_duration)

def should_send_daily_summary(db: Session) -> bool:
    """Check if daily summary was already sent today."""
    # TODO: Implement tracking table for sent summaries
    # For now, always returns True
    return True

def mark_summary_sent(db: Session):
    """Mark that today's summary was sent."""
    # TODO: Insert record into tracking table
    pass 

def send_with_retry(func, *args, max_retries=3, **kwargs):
    """Retry wrapper for email sending."""
    for attempt in range(max_retries):
        try:
            func(*args, **kwargs)
            return # Success
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error("Failed to send after %d attemps: %s", max_retries, e)
                raise
            else:
                logger.warning("Attempt %d failed, retrying: %s", attempt + 1, e)
                time.sleep(2 ** attempt) # Exponential backoff