from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .common import InstrumentResponseForPart, PartResponseForInstrument


class PartBase(BaseModel):
    """Base schema for part data."""
    part_number: str = Field(..., min_length=1,
                             max_length=100, description="Unique part number")
    name: str = Field(..., min_length=1, max_length=200,
                      description="Part name")
    description: Optional[str] = Field(None, description="Part description")
    category: Optional[str] = Field(
        None, max_length=100, description="Part category")
    manufacturer: Optional[str] = Field(
        None, max_length=100, description="Manufacturer name")
    quantity_in_stock: int = Field(
        0, ge=0, description="Current stock quantity")
    minimum_stock_level: int = Field(
        0, ge=0, description="Minimum stock level")
    is_critical: bool = Field(False, description="Is this a critical part")


class PartCreate(PartBase):
    """Schema for creating a new part."""
    instrument_id: Optional[int] = Field(
        None, description="Optional ID of the instrument to link this part to upon creation.")


class PartUpdate(BaseModel):
    """Schema for updating a part."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    quantity_in_stock: Optional[int] = Field(None, ge=0)
    minimum_stock_level: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class PartResponse(PartBase):
    """Schema for part response."""
    id: int
    is_active: bool
    stock_status: str
    is_low_stock: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    instruments: List[InstrumentResponseForPart] = []

    class Config:
        from_attributes = True


class StockUpdate(BaseModel):
    """Schema for updating stock quantity."""
    quantity_change: int = Field(
        ..., description="Change in quantity (+ve for add, -ve for remove)")
    reason: Optional[str] = Field(None, description="Reason for stock change")
