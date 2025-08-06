# scripts/create_admin.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# import the necessary components from application
from database import SessionLocal
from models.user import User
from utils.security import get_password_hash
from utils.config import settings
from utils.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)


def create_admin_user():
    """"
    Creates the initial admin user in the database.
    """
    logger.info("Attempting to create admin user...")
    db: Session = SessionLocal()

    try:
        # Check if the admin user or email already exists
        existing_user = db.query(User).filter((User.username == settings.ADMIN_USERNAME) |
                                              (User.email == settings.ADMIN_EMAIL)).first()
        if existing_user:
            logger.warning("User with username '%s' or email '%s' already exists.",
                           settings.ADMIN_USERNAME, settings.ADMIN_EMAIL)
            return

        # Hash the password
        hashed_password = get_password_hash(settings.ADMIN_PASSWORD)

        # Create the new admin user object
        admin_user = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hashed_password=hashed_password,
            first_name=settings.ADMIN_FIRST_NAME,
            last_name=settings.ADMIN_LAST_NAME,
            is_active=True,
            is_admin=True  # CRUCIAL!!!
        )
        # Add admin user to the db
        db.add(admin_user)
        db.commit()

        logger.info("Admin user '%s' created successfully!",
                    settings.ADMIN_USERNAME)

    except IntegrityError:
        db.rollback()
        logger.error(
            "An integrity error occured. The user might have been created in a race condition.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error("An unexpected error occured: %s", e, exc_info=True)

    finally:
        # Close the session
        db.close()


if __name__ == "__main__":
    # This makes the script runnable from CLI
    create_admin_user()
