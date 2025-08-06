from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InstrumentPartBase(BaseModel):
    """Base schema for instrument-part relationship."""
    instrument_id: int = Field(..., description="Instrument ID")
    part_id: int = Field(..., description="Part ID")
    quantity_required: int = Field(1, ge=1, description="Quantity required")
    is_critical: bool = Field(
        False, description="Is this part critical for the instrument")
    installation_notes: Optional[str] = Field(
        None, description="Installation notes")


class InstrumentPartCreate(InstrumentPartBase):
    """Schema for creating instrument-part relationship."""
    pass


class InstrumentPartResponse(InstrumentPartBase):
    """Schema for instrument-part response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
