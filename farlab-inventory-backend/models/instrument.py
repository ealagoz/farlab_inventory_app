# Instrument table (MAT253, Kiel IV, etc.)
from sqlalchemy import Column, Integer, Boolean, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class Instrument(Base):
    """
    Instrument model representing laboratory instruments like MAT253, Kiel IV, etc.
    """
    __tablename__ = "instruments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Instrument basic information
    name = Column(String(100), nullable=False, unique=True, index=True)
    model = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    serial_number = Column(String(100), nullable=False, unique=True)

    # Instrument details
    description = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)

    # Status and operational information
    is_active = Column(Boolean, default=True, nullable=False)
    # Operatinal, maintenance, out_of_service
    status = Column(String(50), default="operational", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)

    # Relationships
    instrument_parts = relationship(
        "InstrumentPart", back_populates="instrument", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"Instrument(id={self.id}, "
            f"name={self.name}, "
            f"model={self.model}, "
            f"manufacturer={self.manufacturer}, "
            f"serial_number={self.serial_number}, "
            f"description={self.description}, "
            f"location={self.location}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at})"
        )

    def __str__(self):
        return (
            f"Instrument(id={self.id}, "
            f"name={self.name}, "
            f"model={self.model}, "
            f"manufacturer={self.manufacturer}, "
            f"serial_number={self.serial_number}, "
        )

    @property
    def parts(self):
        """Get all active parts used by this instrument."""
        return [ip.part for ip in self.instrument_parts if ip.is_critical and ip.is_active]
