from pydantic import BaseModel, Field
from typing import Optional


class InstrumentResponseForPart(BaseModel):
    """A simplified Instrument schema for embedding in Part responses."""
    id: int
    name: str
    model: str
    location: Optional[str]

    class Config:
        from_attributes = True


class PartResponseForInstrument(BaseModel):
    """A simplified Part schema for embedding in Instrument responses."""
    id: int
    part_number: str
    name: str
    quantity_in_stock: int
    is_critical: bool

    class Config:
        from_attributes = True