"""
Database configuration and session management for the FastAPI application.

This module handles the setup of the SQLAlchemy engine, session creation,
and provides a dependency for getting a database session in API endpoints.
It also includes a function to initialize the database tables based on the defined models.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base
from typing import Generator

# Import models for SQLAlchemy table creation.
# These imports are necessary for Base.metadata to discover the tables.
# The 'noqa: F401' comment suppresses unused import warnings from linters.
from models.instrument import Instrument  # noqa: F401
from models.user import User  # noqa: F401
from models.part import Part  # noqa: F401
from models.alert import Alert  # noqa: F401
from models.instrument_part import InstrumentPart  # noqa: F401
from utils.config import settings
from utils.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

# Retrieve the database connection string from environment variables.
if not settings.DATABASE_URL:
    logger.error("DATABASE_URL envinronement variable not set")
    raise ValueError("DATABASE_URL environment variable not set")

# Create the SQLAlchemy engine, which is the entry point to the database.
# This manages connections to the PostgreSQL database.
engine = create_engine(settings.DATABASE_URL)

# Create a configured "Session" class. This is a factory for new Session objects.
# - autocommit=False: We will manually commit transactions.
# - autoflush=False: We will manually flush changes to the DB.
# - bind=engine: Connects this session factory to our database engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """
    Creates all database tables defined in the models.

    This function uses SQLAlchemy's metadata to issue CREATE TABLE statements
    for all tables that do not yet exist in the database. It should be called
    once during application startup.
    """
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session for each request.

    This function creates a new database session for a single request,
    yields it to the endpoint, and ensures that the session is closed
    after the request is finished, even if an error occurs.

    Yields:
        Session: The SQLAlchemy database session.
    """
    # Create a new database session
    db = SessionLocal()
    try:
        # Yield the session to the calling function (the API endpoint)
        yield db
    finally:
        # Always close the session when the request is done
        db.close()
