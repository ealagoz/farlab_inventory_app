from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Annotated, Optional

from database import get_db
from models.part import Part
from models.alert import Alert
from models.instrument import Instrument
from models.user import User
from models.instrument_part import InstrumentPart
from schemas.part import PartCreate, PartResponse, StockUpdate, PartUpdate
from utils.dependencies import get_current_user, get_current_admin_user
from utils.logging_config import get_logger
from utils.config import settings
from services import alert_service
from services.notification_service import send_low_stock_email_notification

router = APIRouter(
    prefix="",
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
    part_data = part.model_dump(exclude={"instrument_id", "instrument_ids"})
    db_part = Part(**part_data)

    # Handle both single and multiple instrument association
    instrument_ids_to_process = []

    logger.info("=== CREATE PART DEBUG ===")
    logger.info(f"Received part data: {part}")
    logger.info(
        f"part.instrument_id: {getattr(part, 'instrument_id', 'NOT_SET')}")
    logger.info(
        f"part.instrument_ids: {getattr(part, 'instrument_ids', 'NOT_SET')}")

    # Prioritize instrument_ids (multiple) over instrument_id (single)
    # New multiple instruments
    if part.instrument_ids and len(part.instrument_ids) > 0:
        instrument_ids_to_process = part.instrument_ids
        logger.info(f"Using multiple instruments: {part.instrument_ids}")
    elif part.instrument_id:  # Legacy single instrument
        instrument_ids_to_process = [part.instrument_id]
        logger.info(f"Using single instrument: {part.instrument_id}")
    else:
        logger.info("No instruments specified")

    logger.info(f"instrument_ids_to_process: {instrument_ids_to_process}")
    logger.info("========================")

    try:
        db.add(db_part)

        # If an instrument_id was passed, create the link.
        if instrument_ids_to_process:
            # Create the association in the InstrumentPart table.
            # Assumes a default quantity_required of 1. Could be changed later.

            # Flush db session before assigning an ID to db_part
            db.flush()

            for instrument_id in instrument_ids_to_process:
                # Verify instrument exists first
                instrument = db.query(Instrument).filter(
                    Instrument.id == instrument_id).first()
                if not instrument:
                    db.rollback()
                    raise HTTPException(
                        status_code=404,
                        detail=f"Instrument with ID {instrument_id} not found."
                    )
            # Create all associations
            for instrument_id in instrument_ids_to_process:
                logger.info(
                    f"Creating association: part_id={db_part.id}, instrument_id={instrument_id}")
                db_relationship = InstrumentPart(
                    instrument_id=instrument_id,
                    part_id=db_part.id,
                    quantity_required=1,
                    is_critical=False
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
        logger.info("Part %d not found for update.", part_id)
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

# Associate existing part with an instrument


@router.post("/{part_id}/instruments/{instrument_id}", response_model=PartResponse)
def associate_part_with_instrument(
    part_id: int,
    instrument_id: int,
    quantity_required: int = 1,
    is_critical: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Associate an existing part with an instrument."""
    try:
        # Validate both part and instrument exist
        db_part = db.query(Part).filter(Part.id == part_id).first()
        if not db_part:
            logger.warning(
                "Part with ID %d not found for association", part_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        db_instrument = db.query(Instrument).filter(
            Instrument.id == instrument_id).first()
        if not db_instrument:
            logger.warning(
                "Instrument with ID %d not found for association", instrument_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instrument not found"
            )

        # Check if association already exists
        existing_association = db.query(InstrumentPart).filter(
            and_(
                InstrumentPart.part_id == part_id,
                InstrumentPart.instrument_id == instrument_id
            )
        ).first()
        if existing_association:
            logger.info(
                "Association between part %d and instrument %d already exists", part_id, instrument_id)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Part '{db_part.name}' is already associated with instrument '{db_instrument.name}'"
            )

        # Validate quantity_required
        if quantity_required < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantity required must be at least 1"
            )

        # Create the association
        db_association = InstrumentPart(
            instrument_id=instrument_id,
            part_id=part_id,
            quantity_required=quantity_required,
            is_critical=is_critical,
            is_active=True
        )

        db.add(db_association)
        db.commit()
        db.refresh(db_part)  # Refresh to load the new relationship

        logger.info(
            "Successfully associated part %d (%s) with instrument %d (%s). Quantity: %d, Critical: %s",
            part_id, db_part.name, instrument_id, db_instrument.name, quantity_required, is_critical
        )

        return db_part

    except HTTPException as e:
        # Re-reise HTTP exceptions as-is
        raise e

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database error while associating part %d with instrument %d: %s",
                     part_id, instrument_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occured while creating the association"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "Unexpected error while associating part %d with instrumet %d: %s",
            part_id, instrument_id, e, exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occured while creating the association"
        )

# Remove an association between a part and an instrument


@router.delete("/{part_id}/instruments/{instrument_id}")
def dissociate_part_from_instrument(
    part_id: int,
    instrument_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove association between a part and an instrument."""
    try:
        # Validate that both part and instrument exist
        db_part = db.query(Part).filter(Part.id == part_id).first()
        if not db_part:
            logger.warning(
                "Part with ID %d not found for dissociation", part_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        db_instrument = db.query(Instrument).filter(
            Instrument.id == instrument_id).first()
        if not db_instrument:
            logger.warning(
                "Instrument with ID %d not found for dissociation", instrument_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instrument not found"
            )

        # Find the association
        db_association = db.query(InstrumentPart).filter(
            and_(
                InstrumentPart.part_id == part_id,
                InstrumentPart.instrument_id == instrument_id,
                InstrumentPart.is_active
            )
        ).first()

        if not db_association:
            logger.info(
                "No active association found between part %d and instrument %d", part_id, instrument_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active association found between part '{db_part.name}' and instrument '{db_instrument.name}'"
            )

        # Instead of deleting, mark as inactive for audit trail
        # You can choose to actually delete if you prefer: db.delete(db_association)
        db_association.is_active = False

        db.commit()

        logger.info(
            "Successfully dissociated part %d (%s) from instrument %d (%s)",
            part_id, db_part.name, instrument_id, db_instrument.name
        )

        return None

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database error while dissociating part %d from instrument %d: %s",
                     part_id, instrument_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred while removing the association"
        )
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error while dissociating part %d from instrument %d: %s",
                     part_id, instrument_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while removing the association"
        )

# Update the association details between a part and an instrument


@router.put("/{part_id}/instruments/{instrument_id}")
def update_part_instrument_association(
    part_id: int,
    instrument_id: int,
    quantity_required: Optional[int] = None,
    is_critical: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the relationship between a part and an instrument."""
    try:
        # Validate that both part and instrument exist
        db_part = db.query(Part).filter(Part.id == part_id).first()
        if not db_part:
            logger.warning(
                "Part with ID %d not found for association update", part_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        db_instrument = db.query(Instrument).filter(
            Instrument.id == instrument_id).first()
        if not db_instrument:
            logger.warning(
                "Instrument with ID %d not found for association update", instrument_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Instrument not found"
            )

        # Find the association
        db_association = db.query(InstrumentPart).filter(
            and_(
                InstrumentPart.part_id == part_id,
                InstrumentPart.instrument_id == instrument_id,
                InstrumentPart.is_active
            )
        ).first()

        if not db_association:
            logger.info("No active association found between part %d and instrument %d for update",
                        part_id, instrument_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active association found between part '{db_part.name}' and instrument '{db_instrument.name}'"
            )

        # Check if at least one field is provided for update
        if quantity_required is None and is_critical is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field (quantity_required or is_critical) must be provided for update"
            )

        # Track what's being updated for logging
        updates_made = []

        # Update quantity_required if provided
        if quantity_required is not None:
            if quantity_required < 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Quantity required must be at least 1"
                )
            old_quantity = db_association.quantity_required
            db_association.quantity_required = quantity_required
            updates_made.append(
                f"quantity_required: {old_quantity} → {quantity_required}")

        # Update is_critical if provided
        if is_critical is not None:
            old_critical = db_association.is_critical
            db_association.is_critical = is_critical
            updates_made.append(f"is_critical: {old_critical} → {is_critical}")

        db.commit()
        db.refresh(db_part)  # Refresh to load updated relationships

        logger.info(
            "Successfully updated association between part %d (%s) and instrument %d (%s). Changes: %s",
            part_id, db_part.name, instrument_id, db_instrument.name, ", ".join(
                updates_made)
        )

        return db_part

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database error while updating association between part %d and instrument %d: %s",
                     part_id, instrument_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred while updating the association"
        )
    except Exception as e:
        db.rollback()
        logger.error("Unexpected error while updating association between part %d and instrument %d: %s",
                     part_id, instrument_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the association"
        )


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

    try:
        # First, resolve or delete related alerts
        alerts = db.query(Alert).filter(Alert.part_id == part_id).all()
        for alert in alerts:
            db.delete(alert)  # Delete alerts instead of trying to resolve them

        # Then delete the part
        db.delete(db_part)
        db.commit()
        return None

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Error deleting part %d: %s", part_id, e)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete part due to database error"
        )

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

    try:
        # Get state before update
        was_low_stock = db_part.is_low_stock

        # Update stock
        db_part.update_stock(stock_update.quantity_change)

        # Handle alerts
        if stock_update.quantity_change > 0 and not db_part.is_low_stock and was_low_stock:
            # Stock replenished - resolve alerts
            alert_service.resolve_alerts_for_part(db, part_id)

        elif db_part.is_low_stock:
            # Check if alert already exists
            existing_alert = db.query(Alert).filter(
                Alert.part_id == part_id,
                Alert.is_active.is_(True)
            ).first()

            if not existing_alert:
                # Create new alert
                new_alert = Alert.create_low_stock_alert(db_part)
                db.add(new_alert)

                # Queue email notification for background
                background_tasks.add_task(
                    send_low_stock_email_notification,
                    part=db_part,
                    admin_email=settings.ADMIN_EMAIL
                )

        # Commit everything atomically
        db.commit()
        db.refresh(db_part)

        return db_part

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to update stock for part {part_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update stock"
        )

# --- PUBLIC ENDPOINTS ---
# Search for parts (requires user to be logged in)


@router.get("/search/", response_model=List[PartResponse])
def search_parts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query for parts")
):
    """Search for parts by name or part number (authenticated users only)."""
    # Sanitize search input
    q = q.strip()
    if len(q) < 2:  # Prevent overly broad searches
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )

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
