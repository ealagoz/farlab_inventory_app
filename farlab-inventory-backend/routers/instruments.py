# /routers/instruments.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Annotated

from database import get_db
from models.instrument import Instrument
from models.user import User
from models.part import Part
from schemas.instrument import InstrumentCreate, InstrumentUpdate, InstrumentResponse
from models.instrument_part import InstrumentPart
from schemas.instrument_part import InstrumentPartCreate, InstrumentPartResponse
from utils.dependencies import get_current_user, get_current_admin_user
from utils.logging_config import get_logger

# Create a new router
router = APIRouter(
    prefix="/api/instruments",
    tags=["Instruments"],
)

# Get a logger for this module
logger = get_logger(__name__)

# --- AUTHENTICATED ENDPOINTS ---
# Create an instrument (required user to be logged in)


@router.post("/", response_model=InstrumentResponse,
             status_code=status.HTTP_201_CREATED)
def create_instrument(
    instrument: InstrumentCreate,
    # User dependency
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Create a new instrument."""
    db_instrument = Instrument(**instrument.model_dump())
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument

# Update an existing instrument (requires user to be logged in)


@router.patch("/{instrument_id}", response_model=InstrumentResponse)
def update_instrument(instrument_id: int,
                      instrument_update: InstrumentUpdate,
                      current_user: Annotated[User, Depends(get_current_user)],
                      db: Session = Depends(get_db)):
    """Update an existing instrument."""
    db_instrument = db.query(Instrument).filter(
        Instrument.id == instrument_id).first()
    if not db_instrument:
        logger.warning(
            "Instrument with ID %d not found for update.", instrument_id)
        raise HTTPException(status_code=404, detail="Instrument not found")
    # Get the updated data, excluding any unset fields
    update_data = instrument_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_instrument, key, value)

    db.commit()
    db.refresh(db_instrument)
    return db_instrument

# Delete an instrument (requires admin user)


@router.delete("/{instrument_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instrument(
    instrument_id: int,
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """Delete an instrument."""
    db_instrument = db.query(Instrument).filter(
        Instrument.id == instrument_id).first()
    if not db_instrument:
        logger.warning(
            "Instrument with ID %d not found for deletion.", instrument_id)
        raise HTTPException(status_code=404, detail="Instrument not found")

    db.delete(db_instrument)
    logger.info("Instrument with ID %d was deleted by admin %d.", instrument_id,
                current_admin_user.id)
    db.commit()
    return None

# --- PUBLIC ENDPOINTS ---
# Get all active instruments (publicly accessible)


@router.get("/", response_model=List[InstrumentResponse])
def get_all_instruments(db: Session = Depends(get_db)):
    """Get all active instruments."""
    instruments = db.query(Instrument).filter(Instrument.is_active).all()
    return instruments

# Get a specific instrument by ID (publicly accessible)


@router.get("/{instrument_id}", response_model=InstrumentResponse)
def get_instrument_by_id(instrument_id: int, db: Session = Depends(get_db)):
    """Get a specific instrument by its ID."""
    instrument = db.query(Instrument).filter(
        Instrument.id == instrument_id).first()
    if not instrument:
        logger.warning("Instrument with ID %d not found.", instrument_id)
        raise HTTPException(status_code=404, detail="Instrument not found")
    return instrument

# Instrument-Part relationship endpoint


@router.post("/instruments/{instrument_id}/parts/{part_id}",
             response_model=InstrumentPartResponse)
async def link_instrument(
    instrument_id: int,
    part_id: int,
    relationship: InstrumentPartCreate,
    db: Session = Depends(get_db)
):
    """Link an instrument to a part with a specific quantity and role."""
    # Check if instrument and part exist
    instrument = db.query(Instrument).filter(
        Instrument.id == instrument_id).first()
    part = db.query(Part).filter(Part.id == part_id).first()

    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
    try:

        # Create the relationship
        db_relationship = InstrumentPart(
            instrument_id=instrument_id,
            part_id=part_id,
            quantity_required=relationship.quantity_required,
            is_critical=relationship.is_critical,
        )
        db.add(db_relationship)
        db.commit()
        db.refresh(db_relationship)

        return db_relationship

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Failed to link instrument %d and part %d due to DB error: %s", instrument_id, part_id,
                     e, exc_info=True)
        raise HTTPException(
            status_code=400, detail=f"Failed to link instrument and part: {str(e)}")
