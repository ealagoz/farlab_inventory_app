# FASTAPI dependency injection
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timezone

from database import get_db
from models.user import User
from utils.security import decode_access_token
from utils.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

# This tells FASTAPI where to look for token
# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl=auth_router.router.url_path_for("token"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


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
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing subject claim")
            raise credentials_exception
    
        # Validate token hasnot expired (decode_access_token should handle this)
        exp = payload.get("exp")
        if not exp or datetime.now(timezone.utc).timestamp() > exp:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Convert user_id back to int if stored as string
        try:
            user_id = int(user_id)
        except ValueError:
            logger.warning("Invalid user ID in token: %s", user_id)
            raise credentials_exception
    except HTTPException:
        raise # Re-raise HTT exceptions
    except Exception as e:  # Catches JWTError from decode_access_token
        logger.warning("Token validation failed: %s", str(e))
        raise credentials_exception

    # Query by ID instead of username for better performance
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.warning("User not found for token: %s", user_id)
        raise credentials_exception

    if not user.is_active:
        logger.warning("Inactive user attempted access: %s", User.username)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is inactive"
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
