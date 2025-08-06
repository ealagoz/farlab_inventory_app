# utils/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file at the applications's root
load_dotenv()


class Settings(BaseSettings):
    """"
    Manages application settings and secrets loaded from .env variables.
    Pydantic will automatically validate that all required variables are present
    on startup.
    """
    # --- Database ---
    HOST: str
    PORT: int
    USERNAME: str
    PASSWORD: str
    DBNAME: str
    DATABASE_URL: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_FIRST_NAME: str
    ADMIN_LAST_NAME: str

    # -- Frontend ---
    FRONTEND_URL: str

    # --- Security & JWT ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Email & Notifications ---
    ADMIN_EMAIL: str
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SENDER_EMAIL: str

    # --- Scheduler ---
    SCHEDULER_INTERVAL_MINUTES: int = 60

    class Config:
        # This tells Pydantic to read variables from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # This tells Pydantic to be case-insensitive when matching env variables
        case_sensitive = False


# Create a single, importable instance of the settings
settings = Settings()
