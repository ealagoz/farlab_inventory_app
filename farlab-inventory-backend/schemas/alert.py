from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertBase(BaseModel):
    """Base schema for alert data."""
    part_id: int = Field(..., description="ID of the part this alert is for")
    message: str = Field(..., description="Alert message")
    current_stock: int = Field(..., ge=0, description="Current stock level")
    threshold_stock: int = Field(..., ge=0,
                                 description="Threshold stock lecel")


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    pass


class AlertResponse(AlertBase):
    """Schema for alert response."""
    id: int
    is_active: bool
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertWithPartInfo(AlertResponse):
    """Scheme for alert response with part information."""
    part_name: str
    part_number: str
    part_manufacturer: Optional[str]
    part_category: Optional[str]


class AlertSummary(BaseModel):
    """Schema for alert summary statistics."""
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    critical_parts_low: int
    out_of_stock_parts: int


class AlertResolve(BaseModel):
    """Schema for resolving an alert."""
    resolution_notes: Optional[str] = Field(
        None, description="Notes about how the alert was resolved")
