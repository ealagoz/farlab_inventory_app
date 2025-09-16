# utils/create_admin.py
"""
Utility functions for creating admin users during application startup.
"""
from sqlalchemy.orm import Session
from models.user import User
from utils.security import get_password_hash
from utils.config import settings
from utils.logging_config import get_logger

logger = get_logger(__name__)


def get_admin_password():
    """
    Get the admin password from environment variables or secret file.
    Priority:
    1. ADMIN_PASSWORD environment variable
    2. ADMIN_PASSWORD_FILE secret file
    3. Default fallback password
    """
    password = getattr(settings, "ADMIN_PASSWORD", None)

    if password and password.startswith("/run/secrets/"):
        # It's a file path, read from the file
        try:
            with open(password, "r") as f:
                password = f.read().strip()
                logger.info("Admin password loaded from secret file")
        except FileNotFoundError:
            logger.warning(f"Admin password file {password} not found")
            password = None
    elif password:
        logger.info("Admin password loaded from environment variable")

    # Fallback to a default password if nothing is found
    if not password:
        password = "admin123"  # Default password - should be changed!
        logger.warning(
            "Using default admin password 'admin123' - CHANGE THIS IN PRODUCTION!")

    return password


def create_admin_user(db: Session) -> bool:
    """
    Create an initial admin user if one doesn't exist.

    Args:
        db: Database session

    Returns:
        bool: True if admin user was created, False if already exists
    """
    try:
        # Check if any admin user already exists
        existing_admin = db.query(User).filter(User.is_admin == True).first()

        if existing_admin:
            logger.info(
                f"Admin user already exists: {existing_admin.username}")
            return False

        # Check if user with admin username already exists
        admin_username = getattr(settings, "ADMIN_USERNAME", "admin")
        existing_user = db.query(User).filter(
            User.username == admin_username).first()

        if existing_user:
            # User exists but is not admin, make them admin
            existing_user.is_admin = True
            db.commit()
            logger.info(f"Made existing user '{admin_username}' an admin")
            return True

        # Create new admin user
        admin_password = get_admin_password()
        hashed_password = get_password_hash(admin_password)

        admin_user = User(
            username=getattr(settings, "ADMIN_USERNAME", "admin"),
            email=getattr(settings, "ADMIN_EMAIL", "admin@example.com"),
            first_name=getattr(settings, "ADMIN_FIRST_NAME", "Admin"),
            last_name=getattr(settings, "ADMIN_LAST_NAME", "User"),
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
            department="System Administrator",
            position="Administrator"
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        logger.info(f"✅ Created admin user: {admin_user.username}")
        logger.info(f"   - Email: {admin_user.email}")
        logger.info(
            f"   - Name: {admin_user.first_name} {admin_user.last_name}")
        logger.info("🔐 Use the credentials above to log into the frontend")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to create admin user: {e}")
        db.rollback()
        raise e


def ensure_admin_exists(db: Session):
    """
    Ensure that at least one admin user exists in the system.
    This function should be called during application startup.
    """
    logger.info("🔍 Checking for admin user...")

    try:
        created = create_admin_user(db)
        if created:
            logger.info("✅ Admin user setup completed")
        else:
            logger.info("✅ Admin user already exists")
    except Exception as e:
        logger.error(f"❌ Failed to ensure admin user exists: {e}")
        raise
