from sqlalchemy.orm import declarative_base

# Create a base class for models to inherit from
# All model classes (Instrument, User, etc.) inherits from this Base
Base = declarative_base()
