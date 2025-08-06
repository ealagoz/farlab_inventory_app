# Alert settings and thresholds
from sqlalchemy import Column, Integer, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from models.base import Base


class Alert(Base):
    """
    Simple alert model for low stock warning.
    """
    __tablename__ = "alerts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Related part
    part_id = Column(Integer, ForeignKey("parts.id"),
                     nullable=False, index=True)

    # Alert information
    # Pre-formatted message with part details
    message = Column(Text, nullable=False)
    current_stock = Column(Integer, nullable=False)
    threshold_stock = Column(Integer, nullable=False)

    # Alert status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_resolved = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    part = relationship("Part", backref="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, part_id={self.part_id}, active={self.is_active})>"

    def __str__(self):
        return f"Low Stock Alert: {self.part.name if self.part else 'Unknown Part'}"

    def resolve(self):
        """ Mark alert as resolved."""
        self.is_resolved = True
        self.is_active = False
        self.resolved_at = func.now()

    @classmethod
    def create_low_stock_alert(cls, part):
        """ Create a low stock alert for a part. """
        # Build detailed message with part information
        stock_message = "LOW STOCK ALERT!"
        parts_info = "Parts need to be purchased: \n"
        message_alert = [
            f"{stock_message}",
            f"{parts_info}",
            f"Part Number: {part.part_number}",
            f"Part Name: {part.name}",
            f"Current Stock: {part.quantity_in_stock}",
            f"Minimum Required: {part.minimum_stock_level}",
        ]

        # Add manufacturer info if available
        if part.manufacturer:
            message_alert.append(f"Manufacturer: {part.manufacturer}")

        # Add part number info
        if part.part_number:
            message_alert.append(f"Manufacturer P/N: {part.part_number}")

        # Add instrument usage info
        if part.instruments:
            instrument_names = [inst.name for inst in part.instruments]
            message_alert.append(
                f"Used by instruments: {', '.join(instrument_names)}")

        # Add critical instrument info
        if part.critical_for_instruments:
            critical_names = [
                inst.name for inst in part.critical_for_instruments]
            message_alert.append(f"Critical for: {', '.join(critical_names)}")

        message = "\n".join(message_alert)

        return cls(
            part_id=part.id,
            message=message,
            current_stock=part.quantity_in_stock,
            threshold_stock=part.minimum_stock_level
        )

    @classmethod
    def check_and_create_alerts(cls, db_session):
        """
        Check all parts and create alerts for those below threshold. 
        Returns list of newly created alerts.
        """
        from models.part import Part

        # Find parts that are low on stock and donot already have active alerts
        low_stock_parts = db_session.query(Part).filter(
            Part.quantity_in_stock <= Part.minimum_stock_level,
            Part.is_active,
            ~Part.id.in_(
                db_session.query(cls.part_id).filter(cls.is_active)
            )
        ).all()

        new_alerts = []
        for part in low_stock_parts:
            alert = cls.create_low_stock_alert(part)
            db_session.add(alert)
            new_alerts.append(alert)

        if new_alerts:
            db_session.commit()

        return new_alerts

    @classmethod
    def resolve_alerts_for_parts(cls, db_session, part_id: int):
        """
        Resolve all active alerts for a part (when stock is replenished).
        """
        alerts = db_session.query(cls).filter(
            cls.part_id == part_id,
            cls.is_active
        ).all()

        for alert in alerts:
            alert.resolve()

        if alerts:
            db_session.commit()

        return len(alerts)
