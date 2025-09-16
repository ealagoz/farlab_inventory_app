# Update farlab-inventory-backend/utils/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv
from .secret_manager import secret_manager
from .logging_config import get_logger
import traceback
import os

# Get logger for this module
logger = get_logger(__name__)

# First, try to import and run SecretManager
try:
    # Force load secrets
    secret_manager.load_secrets()

    # Debug: check what secrets were loaded
    secret_vars = ['POSTGRES_PASSWORD', 'ADMIN_PASSWORD', 'PASSWORD', 'SECRET_KEY',
                   'SMTP_USER', 'SMTP_PASSWORD', 'ADMIN_EMAIL', 'SENDER_EMAIL']
    for var in secret_vars:
        value = os.environ.get(var)
        logger.error(f"{var}: {'✅ SET' if value else '❌ NOT SET'}")

except Exception as e:
    logger.error(f"❌ Error with SecretManager: {e}")
    traceback.print_exc()

# Then load .env file for non-sensitive configuration
dotenv_path = find_dotenv()
if dotenv_path:
    logger.info(f"Loading .env file from: {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print("Warning: .env file not found")


class Settings(BaseSettings):
    # General settings
    APP_NAME: str = "FARLAB Inventory Management System"
    DEBUG: bool = False  # Set to false for production
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Database ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str
    POSTGRES_PASSWORD: str = ""  # Make optional
    DB_NAME: str
    DATABASE_URL: str = ""  # Make optional
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str = ""  # Make optional
    ADMIN_FIRST_NAME: str
    ADMIN_LAST_NAME: str
    PASSWORD: str = ""  # Make optional
    API_PREFIX: str = "/api"  # Default value

    # --- Security & JWT ---
    SECRET_KEY: str  # From secrets
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Email & Notifications ---
    ADMIN_EMAIL: str  # From secrets
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str = ""  # Make optional
    SMTP_PASSWORD: str = ""  # Make optional
    SENDER_EMAIL: str = ""  # Make optional

    # --- Scheduler ---
    SCHEDULER_INTERVAL_MINUTES: int = 60

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore"
    )


try:
    settings = Settings()
    logger.info("✅ Settings created successfully!")

except Exception as e:
    logger.error(f"❌ Error creating Settings: {e}")

    # Show what environment variables are actually available
    for key, value in sorted(os.environ.items()):
        if any(secret in key.upper() for secret in ['PASSWORD', 'SECRET', 'SMTP', 'EMAIL']):
            logger.info(f"{key}: {'SET' if value else 'EMPTY'}")

    raise
