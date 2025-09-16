# Threshold checking and notification triggers
# services/alert_service.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import BackgroundTasks, Depends

from models.part import Part
from schemas.alert import AlertSummary
from services.notification_service import send_low_stock_email_notification
from utils.dependencies import get_db
from utils.logging_config import get_logger
from utils.config import settings
from models.alert import Alert

# Get a logger for this module
logger = get_logger(__name__)


def get_alerts(db: Session, skip: int, limit: int = 100, active_only: bool = True):
    """"
    Fetches alerts from database for UI.
    Can fetch only active alerts or all alerts.
    """
    query = db.query(Alert)
    if active_only:
        query = query.filter(Alert.is_active.is_(True))

    return query.order_by(Alert.created_at.desc()).populate_existing().offset(skip).limit(limit).all()


def check_stock_and_create_alert(db: Session, part_id: int, background_tasks: BackgroundTasks, user_email: str):
    """"
    Checks the stock level of a part and sends an alert if it's low.
    This is to be called after a part's quantity is updated.
    """
    # Fetch part directly from database
    part = db.query(Part).filter(Part.id == part_id).first()

    if not part or not part.is_low_stock:
        return  # part doesnot exist or stock is fine, do nothing.

    # Check if an active alert already exists for this part
    existing_alert = db.query(Alert).filter(
        Alert.part_id == part_id, Alert.is_active.is_(True)).first()
    if existing_alert:
        return  # An active alert exists so do nothing.

    # If stock is low AND no active alert exists.
    logger.info("Part '%s' is low on stock. Creating new alert.", part.name)

    # Create the alert object and save it to the db
    try:
        new_alert = Alert.create_low_stock_alert(part)
        db.add(new_alert)
        db.commit()
        logger.info(
            "New alert for part '%s' created and committed to the database.", part.name)
    except IntegrityError:
        db.rollback()
        logger.info(
            "Active alert already exists for part '%s', skipping", part_id)

    # Que the email to be sent in the background
    background_tasks.add_task(
        send_low_stock_email_notification,
        part=part,
        admin_email=settings.ADMIN_EMAIL
    )


def get_low_stock_parts(db: Session) -> list[Part]:
    """"
    Returns a list of all parts that are currently low on stock.
    """
    return db.query(Part).filter(Part.quantity_in_stock <= Part.minimum_stock_level).all()


def get_alert_summary(db: Session = Depends(get_db)):
    """"
    Get a summary of the current alert status, including counts for low
    stock and out of stock parts.
    """
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.is_active.is_(True)).count()
    resolved_alerts = db.query(Alert).filter(
        Alert.is_resolved.is_(True)).count()

    # Count parts that are out of stock
    out_of_stock_parts = db.query(Part).filter(
        Part.quantity_in_stock == 0,
        Part.is_active.is_(True)
    ).count()

    # Count critical parts that are low on stock BUT not out of stock
    critical_parts_low = db.query(Part).filter(
        Part.is_critical.is_(True),
        Part.quantity_in_stock <= Part.minimum_stock_level,
        Part.quantity_in_stock > 0,
        Part.is_active.is_(True)
    ).count()

    return AlertSummary(
        total_alerts=total_alerts,
        active_alerts=active_alerts,
        resolved_alerts=resolved_alerts,
        critical_parts_low=critical_parts_low,
        out_of_stock_parts=out_of_stock_parts
    )


def resolve_alerts_for_part(db: Session, part_id: int):
    """"
    Finds and resolves all active alerts for a specific part.
    This should be called when stock is replenished.
    """
    alerts_to_resolve = db.query(Alert).filter(
        Alert.part_id == part_id, Alert.is_active.is_(True)).all()
    if not alerts_to_resolve:
        return

    logger.info("Stock replenished for part ID %d. Resolving %d active alert(s).",
                part_id, len(alerts_to_resolve))
    for alert in alerts_to_resolve:
        alert.resolve()

    db.commit()
