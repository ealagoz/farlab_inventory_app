# routers/alerts.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from schemas.alert import AlertResponse, AlertSummary
from schemas.part import PartResponse
from services import alert_service
from utils.dependencies import get_db

router = APIRouter(
    prefix="/api/alerts",
    tags=["Alerts"],
)


@router.get("/", response_model=List[AlertResponse])
def read_alerts(
    active_only: bool = Query(
        True, description="Filter for only active alerts"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of alerts from database.
    This is the primary endpoint for the Alerts UI page.
    """
    alerts = alert_service.get_alerts(
        db=db, skip=skip, limit=limit, active_only=active_only)

    return alerts


@router.get("/low-stock", response_model=List[PartResponse], tags=["Alerts"])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    """"
    Get a list of all parts that are currently low on stock.
    """
    low_stock_parts = alert_service.get_low_stock_parts(db)
    return low_stock_parts


@router.get("/summary", response_model=AlertSummary)
def get_alert_summary(db: Session = Depends(get_db)):
    """"
    Get alert summary statistics by called the alert service.
    """
    summary = alert_service.get_alert_summary(db)
    return summary
