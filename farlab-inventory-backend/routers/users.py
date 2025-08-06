# /users/ CRUD endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Annotated

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from utils.dependencies import get_current_user, get_current_admin_user
from utils.logging_config import get_logger
from utils.security import get_password_hash

# Create a new router
router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    # All routes in this router require authentication
    dependencies=[Depends(get_current_user)]
)

# Get a logger for this module
logger = get_logger(__name__)

# Note: User creation is a protected endpoint
# In public app, get a separate, unprotected "signup" router

# Create a new user (admin only)


@router.post("/", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """Create a new user."""
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if existing_user:
        logger.warning(
            "User creation failed: username or email for '%s' already exists.", user.username)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    hashed_password = get_password_hash(user.password)
    db_user = User(
        **user.model_dump(exclude={"password"}),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get currentnly logged in user profile


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get the profile of the currently logged-in user"""
    return current_user

# Update currently logged-in user profile


@router.patch("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Update the profile of the currently logged-in user."""
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

# Get all users (admin only)


# @router.get("/{user_id}", response_model=List[UserResponse])
@router.get("/", response_model=List[UserResponse])
def get_all_users(
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """Get a list of all users."""
    users = db.query(User).all()
    return users

# Get a specific user by ID (admin only)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """Get a specific user by their ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning("User with ID %d not found.", user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Delete a user (admin only)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    db: Session = Depends(get_db)
):
    """Delete a user."""
    # Prevent an admin from deleting themselves
    if current_admin_user.id == user_id:
        logger.warning("Admin user %d attempted to delete their own account.",
                       current_admin_user.id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot delete their own account"
        )
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning("User with ID %d not found for deletion.", user_id)
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    logger.info("User with ID %d was deleted by admin %d.", user_id,
                current_admin_user.id)
    db.commit()
    return None
