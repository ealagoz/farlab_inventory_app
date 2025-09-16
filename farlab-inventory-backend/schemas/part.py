from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .common import InstrumentResponseForPart


class PartBase(BaseModel):
    """Base schema for part data."""
    part_number: str = Field(..., min_length=1,
                             max_length=100, description="Unique part number")
    name: Optional[str] = Field(None, min_length=1, max_length=200, 
                               description="Updated part name")
    description: Optional[str] = Field(None, 
                                      description="Updated part description")
    category: Optional[str] = Field(None, max_length=100, 
                                   description="Updated part category")
    manufacturer: Optional[str] = Field(None, max_length=100, 
                                       description="Updated manufacturer")
    quantity_in_stock: Optional[int] = Field(None, ge=0, le=100000, 
                                            description="Updated stock quantity")
    minimum_stock_level: Optional[int] = Field(None, ge=0, le=100000, 
                                              description="Updated minimum stock level")
    is_active: Optional[bool] = Field(None, 
                                     description="Updated active status")


class PartCreate(PartBase):
    """Schema for creating a new part."""
    # Support both single and multiple instruments
    instrument_id: Optional[int] = Field(
        None, description="Single instrument ID (legacy)")
    instrument_ids: Optional[List[int]] = Field(
        default=None,
        description="Multiple instrument IDs")


class PartUpdate(BaseModel):
    """Schema for updating a part."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=100)
    quantity_in_stock: Optional[int] = Field(None, ge=0, le=100000)
    minimum_stock_level: Optional[int] = Field(None, ge=0, le=100000)
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
        ...,
        ge=-10000,  # Allow removing up to 10,000 items
        le=10000,   # Allow adding up to 10,000 items
        description="Change in quantity (+ve for add, -ve for remove)")
    reason: Optional[str] = Field(
        None,
        max_length=500,  # Prevent abuse
        description="Reason for stock change")


class PartInstrumentAssociation(BaseModel):
    """Schema for associating a part with an instrument."""
    instrument_id: int = Field(..., gt=0,
                               description="ID of the instrument to associate")
    quantity_required: int = Field(
        1, ge=1, description="Quantity of this part required by the instrument")
    is_critical: bool = Field(
        False, description="Whether this part is critical for the instrument's operation")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "instrument_id": 1,
                "quantity_required": 2,
                "is_critical": True
            }
        }


class PartInstrumentAssociationResponse(BaseModel):
    """Schema for part-instrument association response."""
    id: int
    instrument_id: int
    part_id: int
    quantity_required: int
    is_critical: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PartInstrumentAssociationUpdate(BaseModel):
    """Schema for updating part-instrument association details."""
    quantity_required: Optional[int] = Field(
        None, ge=1, description="Updated quantity required")
    is_critical: Optional[bool] = Field(
        None, description="Updated critical status")

    class Config:
        json_schema_extra = {
            "example": {
                "quantity_required": 3,
                "is_critical": False
            }
        }


class BulkAssociateInstruments(BaseModel):
    """Schema for bulk association of instruments to a part."""
    associations: List[PartInstrumentAssociation] = Field(
        ...,
        min_items=1,
        description="List of instrument associations to create"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "associations": [
                    {
                        "instrument_id": 1,
                        "quantity_required": 2,
                        "is_critical": True
                    },
                    {
                        "instrument_id": 2,
                        "quantity_required": 1,
                        "is_critical": False
                    }
                ]
            }
        }
