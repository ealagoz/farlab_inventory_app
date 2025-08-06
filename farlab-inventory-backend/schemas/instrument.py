from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .common import PartResponseForInstrument, InstrumentResponseForPart


class InstrumentBase(BaseModel):
    """Base schema for instrument data."""
    name: str = Field(..., min_length=1, max_length=100,
                      description="Intrument name")
    model: str = Field(..., min_length=1, max_length=100,
                       description="Instrument model")
    manufacturer: Optional[str] = Field(
        None, max_length=100, description="Manufacturer name")
    serial_number: Optional[str] = Field(
        None, max_length=100, description="Serial number")
    location: Optional[str] = Field(None, description="Instrument location")
    description: Optional[str] = Field(
        None, description="Instrument description")


class InstrumentCreate(BaseModel):
    """Schema for creating a new instrument."""
    pass


class InstrumentUpdate(BaseModel):
    """Schema for updating an instrument."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class InstrumentResponse(InstrumentBase):
    """Schema for instrument response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    parts: List[PartResponseForInstrument] = []

    class Config:
        from_attributes = True  # For SQLAlchemy models



