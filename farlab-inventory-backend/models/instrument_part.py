from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class InstrumentPart(Base):
    """
    Association table linking instruments to their parts. 
    This allows tracking which parts are used in which instruments.
    """
    __tablename__ = "instrument_parts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    instrument_id = Column(Integer, ForeignKey(
        "instruments.id"), nullable=False, index=True)
    part_id = Column(Integer, ForeignKey("parts.id"),
                     nullable=False, index=True)

    # Quantity required
    quantity_required = Column(Integer, nullable=False, default=1)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_critical = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)

    # Relationships
    instrument = relationship("Instrument", back_populates="instrument_parts")
    part = relationship("Part", back_populates="instrument_parts")

    def __repr__(self):
        return f"<InstrumentPart(instrument_id={self.instrument_id}, part_id={self.part_id}, qty={self.quantity_required})>"

    def __str__(self):
        return f"{self.instrument.name if self.instrument else 'Unknown'} uses {self.part.name if self.part else 'Unknown'}"
