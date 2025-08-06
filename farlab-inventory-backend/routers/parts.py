from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Annotated, Optional

from database import get_db
from models.part import Part
from models.user import User
from models.instrument_part import InstrumentPart
from schemas.part import PartCreate, PartResponse, StockUpdate, PartUpdate
from utils.dependencies import get_current_user, get_current_admin_user
from utils.logging_config import get_logger
from services import alert_service

router = APIRouter(
    prefix="/api/parts",
    tags=["Parts"],
)

# Get a logger for this module
logger = get_logger(__name__)

# --- AUTHENTICATED ENDPOINTS ---
# # Create a part (requires user to be logged in)


@router.post("/", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
def create_part(
    part: PartCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new part if an instrument_id is provided, it will also
    create the association between the new part and the instrument."""
    part_data = part.model_dump(exclude={"instrument_id"})
    db_part = Part(**part_data)

    try:
        db.add(db_part)

        # If an instrument_id was passed, create the link.
        if part.instrument_id:
            # Create the association in the InstrumentPart table.
            # Assumes a default quantity_required of 1. Could be changed later.

            # Flush db session before assigning an ID to db_part
            db.flush()

            db_relationship = InstrumentPart(
                instrument_id=part.instrument_id,
                part_id=db_part.id,
                quantity_required=1
            )
            db.add(db_relationship)
        db.commit()
        # Refresh the part again to load the new relationship into its 'instruments' list
        db.refresh(db_part)
        return db_part

    except IntegrityError as e:
        db.rollback()  # Rollback the failed transaction
        logger.warning("Integrity error while creating part: %s", e)
        # Check if the error message contains the name of uniq constraints
        if "ix_parts_part_number" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,  # 409 is for conflict
                detail=f"A part with a part number '{part.part_number}' already exists. Please use a different part number."
            )
        # If it is another integrity error, raise a generic message.
        raise HTTPException(
            status_code=500,
            detail="A database integrity error occured."
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("ERROR: Could not create part: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occured while creating the part"
        )


# Update part (requires user to be logged in)


@router.patch("/{part_id}", response_model=PartResponse)
def update_part(
    part_id: int,
    part_update: PartUpdate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update an existing part."""
    db_part = db.query(Part).filter(Part.id == part_id).first()
    if not db_part:
        logger.info("Part %d stock updated. Resolving alerts.", part_id)
        raise HTTPException(status_code=404, detail="Part not found")

    # Get the state of the stock BEFORE making any changes
    quantity_before_update = db_part.quantity_in_stock

    update_data = part_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_part, key, value)

    db.commit()
    db.refresh(db_part)

    # If stock levels were changed, check for alerts
    if "quantity_in_stock" in update_data or "minimum_stock_level" in update_data:
        # 1. Handle RESOLVING alerts.
        # If stock was added and the part is no longer low...
        logger.info(
            "Part %d is low on stock. Checking for alert creation.", part_id)
        if db_part.quantity_in_stock > quantity_before_update and not db_part.is_low_stock:
            logger.info(
                "Part '%d' stock updated and is no longer low. Resolving alerts.", part_id)
            alert_service.resolve_alerts_for_part(db, part_id)

        # 2. Handle CREATING alerts.
        # If the part is currently in a low stock state...
        if db_part.is_low_stock:
            logger.info(
                "Part '%d' is low on stock after update. Checking for alert creation.", part_id)

            alert_service.check_stock_and_create_alert(
                db=db,
                part_id=part_id,
                background_tasks=background_tasks,
                user_email=current_user.email
            )

    return db_part

# Delete a part (requires admin user)


@router.delete("/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_part(
    part_id: int,
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """Delete a part."""
    db_part = db.query(Part).filter(Part.id == part_id).first()
    if not db_part:
        raise HTTPException(status_code=404, detail="Part not found")

    db.delete(db_part)
    db.commit()
    return None

# Update stock quantity for a part (requires user to be logged in)


@router.post("/{part_id}/stock", response_model=PartResponse)
def update_stock_level(
    part_id: int,
    stock_update: StockUpdate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update the stock quantity for a part and mange alerts."""
    db_part = db.query(Part).filter(Part.id == part_id).first()
    if not db_part:
        logger.warning("Part with ID %d not found for stock update.", part_id)
        raise HTTPException(status_code=404, detail="Part not found")

    db_part.update_stock(stock_update.quantity_change)
    db.commit()
    db.refresh(db_part)

    # If stock was added AND the part is no longer in a low stock state...
    if stock_update.quantity_change > 0 and not db_part.is_low_stock:
        # ...then resolve any active alerts for it.
        alert_service.resolve_alerts_for_part(db, part_id)
    # Else if the part is in a low stock state...
    elif db_part.is_low_stock:
        # ...check if a new alert needs to be created.
        alert_service.check_stock_and_create_alert(
            db=db,
            part_id=part_id,
            background_tasks=background_tasks,
            user_email=current_user.email)

    return db_part

# --- PUBLIC ENDPOINTS ---
# Search for parts (publicly accessible)


@router.get("/search/", response_model=List[PartResponse])
def search_parts(
    q: str = Query(..., min_length=1, description="Search query for parts"),
    db: Session = Depends(get_db)
):
    """Search for parts by name or part number."""
    search_term = f"%{q}%"
    parts = db.query(Part).filter(
        Part.is_active,
        or_(
            Part.name.ilike(search_term),
            Part.part_number.ilike(search_term)
        )
    ).all()
    return parts

# Get all active parts (publicly accessible)


@router.get("/", response_model=List[PartResponse])
def get_all_parts(
    db: Session = Depends(get_db),
    instrument_id: Optional[int] = None
):
    """Get all active parts. Can be filtered by instrument ID."""
    query = db.query(Part).filter(Part.is_active)

    if instrument_id:
        query = query.join(InstrumentPart).filter(
            InstrumentPart.instrument_id == instrument_id)

    parts = query.all()
    return parts


# Get a specific part by its ID (publicly accessible)


@router.get("/{part_id}", response_model=PartResponse)
def get_part_by_id(part_id: int, db: Session = Depends(get_db)):
    """Get a specific part by its ID."""
    part = db.query(Part).filter(Part.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    return part
