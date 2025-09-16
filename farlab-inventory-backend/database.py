"""
Database configuration and session management for the FastAPI application.

This module handles the setup of the SQLAlchemy engine, session creation,
and provides a dependency for getting a database session in API endpoints.
It also includes a function to initialize the database tables based on the defined models.
"""

# Standard library imports
import os
from contextlib import contextmanager
from typing import Generator
from urllib.parse import quote_plus

# Third-party imports
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# Local imports
from models.base import Base
from utils.config import settings
from utils.logging_config import get_logger

# Initialize logging
logger = get_logger(__name__)

#------------------------------------------------------------------------------
# Constants and Global Variables
#------------------------------------------------------------------------------
# Initialize as None for lazy loading
background_engine = None
BackgroundSessionLocal = None
DATABASE_URL = None
engine = None
SessionLocal = None

#------------------------------------------------------------------------------
# Configuration and Validation
#------------------------------------------------------------------------------
def validate_database_settings():
    """Ensure all required database settings are provided."""
    required_settings = {
        "DB_USER": settings.DB_USER,
        "DB_HOST": settings.DB_HOST,
        "DB_PORT": settings.DB_PORT,
        "DB_NAME": settings.DB_NAME,
        "PASSWORD": settings.PASSWORD
    }
    missing = [name for name, value in required_settings.items() if not value]
    if missing:
        raise ValueError(f"Missing database configuration: {', '.join(missing)}")

def get_pool_settings(is_background: bool = False) -> dict:
    """Return connection pool settings based on usage context."""
    if is_background:
        return {
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 30,
            "pool_recycle": 3600,  # 1 hour
            "pool_pre_ping": True,
            "connect_args": {"application_name": "inventory_scheduler"}
        }
    return {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600,  # 1 hour
        "pool_pre_ping": True
    }

#------------------------------------------------------------------------------
# Database URL Construction
#------------------------------------------------------------------------------
def construct_db_url(password: str) -> str:
    """Construct database URL with proper escaping."""
    return (
        f"postgresql://{settings.DB_USER}:{quote_plus(password)}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

def get_database_url() -> str:
    """
    Construct the database URL from settings with password priority order:
    1. Docker secrets file
    2. Environment variable
    3. Settings fallback
    """
    password_sources = [
        ("Docker secret", lambda: open("/run/secrets/postgres_secret", "r").read().strip() 
            if os.path.exists("/run/secrets/postgres_secret") else None),
        ("Environment", lambda: os.getenv("POSTGRES_PASSWORD")),
        ("Settings", lambda: getattr(settings, "PASSWORD", None))
    ]

    for source_name, get_password in password_sources:
        try:
            if password := get_password():
                logger.info(f"Database password loaded from {source_name}")
                return construct_db_url(password)
        except Exception as e:
            logger.warning(f"Failed to get password from {source_name}: {e}")

    raise ValueError("Database password not found from any source")

#------------------------------------------------------------------------------
# Main Database Setup
#------------------------------------------------------------------------------
def initialize_database():
    """Initialize the main database engine and session maker."""
    global engine, SessionLocal, DATABASE_URL
    
    try:
        validate_database_settings()
        DATABASE_URL = get_database_url()
        engine = create_engine(
            DATABASE_URL,
            **get_pool_settings(is_background=False)
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("Database engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def create_tables():
    """Creates all database tables defined in the models."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully")
    except Exception as e:
        logger.error(f"Could not create database tables: {e}")
        raise

#------------------------------------------------------------------------------
# Session Management
#------------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#------------------------------------------------------------------------------
# Background Job Database Setup
#------------------------------------------------------------------------------
def get_or_create_background_engine():
    """Lazy load the background engine and session maker."""
    global background_engine, BackgroundSessionLocal
    if background_engine is None:
        background_engine = create_engine(
            get_database_url(),
            **get_pool_settings(is_background=True)
        )
        BackgroundSessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=background_engine
        )
    return background_engine

@contextmanager
def get_background_db_session():
    """Context manager for background database sessions."""
    session = None
    try:
        session = BackgroundSessionLocal()
        yield session
    finally:
        if session:
            session.close()

#------------------------------------------------------------------------------
# Monitoring Setup
#------------------------------------------------------------------------------
def setup_engine_monitoring(engine, engine_name: str):
    """Setup connection monitoring for a given engine."""
    @event.listens_for(engine, "connect")
    def log_connection(dbapi_connection, connection_record):
        logger.debug("Database connection established (%s): %s", 
                    engine_name, id(dbapi_connection))

    @event.listens_for(engine, "close")
    def log_disconnection(dbapi_connection, connection_record):
        logger.debug("Database connection closed (%s): %s", 
                    engine_name, id(dbapi_connection))

#------------------------------------------------------------------------------
# Background Jobs
#------------------------------------------------------------------------------
def safe_scheduled_alert_job():
    """Execute scheduled alert job with dedicated background session."""
    from services.notification_service import send_periodic_alert_summary
    from services.alert_service import get_low_stock_parts

    with get_background_db_session() as db:
        try:
            with db.begin():
                low_stock_parts = get_low_stock_parts(db)
                if low_stock_parts:
                    send_periodic_alert_summary(low_stock_parts, settings.ADMIN_EMAIL)
        except Exception as e:
            logger.error("Scheduled job failed: %s", e, exc_info=True)

#------------------------------------------------------------------------------
# Initialize Database and Monitoring
#------------------------------------------------------------------------------
def init_app():
    """Initialize database connections and monitoring."""
    # Initialize main database
    initialize_database()

    # Initialize background engine
    get_or_create_background_engine()

    # Setup monitoring for both engines
    setup_engine_monitoring(engine, "Main")
    setup_engine_monitoring(background_engine, "Background")