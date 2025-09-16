# models/__init__.py
from models.base import Base
from models.user import User
from models.instrument import Instrument
from models.part import Part
from models.instrument_part import InstrumentPart
from models.alert import Alert

# To ensure all models are loaded when any model is imported
__all__ = [
    "Base",
    "User",
    "Instrument",
    "Part",
    "InstrumentPart",
    "Alert",
]