# Parts tables for each instrument type
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class Part(Base):
    """"
    Part model representing inventory parts that can be used accross different instruments.
    """
    __tablename__ = "parts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Part basic information
    part_number = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    # e.g. "Vacuum", "Eletctronics", "Consumables"
    category = Column(String(100), nullable=True, index=True)

    # Manufacturer information
    manufacturer = Column(String(100), nullable=True)

    # Inventory tracking
    quantity_in_stock = Column(Integer, nullable=False, default=0)
    minimum_stock_level = Column(Integer, nullable=False, default=0)
    # e.g. "each", "g", "ml", "L", "m", "m^2"
    unit_of_measure = Column(String(20), default="each", nullable=True)
    # critical parts are parts that need monitoring
    is_critical = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instrument_parts = relationship(
        "InstrumentPart", back_populates="part", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Part(id={self.id}, part_number={self.part_number}, name={self.name}, description={self.description}, category={self.category}, manufacturer={self.manufacturer}, quantity_in_stock={self.quantity_in_stock}, minimum_stock_level={self.minimum_stock_level}, unit_of_measure={self.unit_of_measure}, is_critical={self.is_critical}, created_at={self.created_at}, updated_at={self.updated_at})>"

    def __str__(self):
        return f"{self.part_number} - {self.name}"

    @property
    def is_low_stock(self) -> bool:
        """
        Check if the part is below minimum stock level.
        """
        return self.quantity_in_stock <= self.minimum_stock_level

    @property
    def stock_status(self) -> str:
        """
        Return stock status as string.
        """
        if self.quantity_in_stock == 0:
            return "Out of stock"
        elif self.quantity_in_stock <= self.minimum_stock_level:
            return "Low stock"
        else:
            return "In stock"

    def update_stock(self, quantity_change: int, reason: str = None):
        """
        Update stock quantity with a change amount.
        Positive for additions, negative for usage.
        """
        self.quantity_in_stock += quantity_change
        if self.quantity_in_stock < 0:
            self.quantity_in_stock = 0
            self.is_critical = True
        self.updated_at = func.now()

    @property
    def instruments(self):
        """Get all active instruments that use this part."""
        return [ip.instrument for ip in self.instrument_parts if ip.is_active]

    @property
    def critical_for_instruments(self):
        """Get list of instruments for which this part is critical."""
        return [ip.instrument for ip in self.instrument_parts if ip.is_critical and ip.is_active]
