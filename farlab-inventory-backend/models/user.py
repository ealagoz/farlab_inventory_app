# User table definition and relationships
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from models.base import Base
from utils.security import verify_password


class User(Base):
    """
    User model representing users of the inventory system.
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User basic information
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)

    # User details
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    # e.g. "Professor", "Graduate Student", "Undergraduate Student", "Staff", "Postdoc", "Visiting Scholar", "Other"
    position = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # User authentication
    hashed_password = Column(String(255), nullable=False)

    # User status
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return (
            f"User(id={self.id}, "
            f"username={self.username}, "
            f"email={self.email}, "
            f"first_name={self.first_name}, "
            f"last_name={self.last_name}, "
            f"phone={self.phone}, "
            f"department={self.department}, "
            f"position={self.position}, "
            f"notes={self.notes}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}, "
            f"last_login={self.last_login})"
        )

    def __str__(self):
        return (
            f"first_name={self.first_name}, "
            f"last_name={self.last_name}, "
            f"username={self.username}, "
        )

    def verify_password(self, password: str) -> bool:
        """
        Verify the provided password against the stored hash.
        """
        return verify_password(password, self.hashed_password)
