# FASTAPI dependency injection
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_db
from models.user import User
from schemas.token import TokenData
from utils.security import decode_access_token
from utils.logging_config import get_logger
from routers import auth as auth_router

# Get a logger for this module
logger = get_logger(__name__)

# This tells FASTAPI where to look for token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=auth_router.router.url_path_for("token"))


def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
) -> User:
    """Dependency to get the current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:  # Catches JWTError from decode_access_token
        logger.warning("Token validation failed: %s",
                       credentials_exception.detail)
        raise credentials_exception

    user = db.query(User).filter_by(username=token_data.username).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=400, detail="Inactive user"
        )
    return user


def get_current_admin_user(
        current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to get the current user and ensure they are admin.
    Raises a 403 Forbidden error if the user is not admin.
    """
    if not current_user.is_admin:
        logger.warning("Forbidden: User '%s' is not an admin.",
                       current_user.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesnot have admin privileges."
        )
    return current_user
