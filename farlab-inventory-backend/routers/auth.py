# /auth/login and /auth/register endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timezone
from uuid import uuid4
import asyncio
import time

from database import get_db
from models.user import User
from utils.dependencies import get_current_user
from utils.security import verify_password, create_access_token, get_password_hash
from schemas.token import Token
from utils.logging_config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

# Create a new router
router = APIRouter(
    prefix="",
    tags=["Authentication"]
)

# Pre-generate a proper dummy hash for timing attack prevention
DUMMY_HASH = get_password_hash("dummy_password_for_timing_attack_on_farlab_inventory_2025")

# @router.post("/token", response_model=Token, name="token") # Original changed 2/9/2025
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    # Start timing
    start_time = time.time()

    # Allways query database
    user = db.query(User).filter(User.username == form_data.username).first()

    # Always perform password verification (even if user doesnot exist)
    if user and user.hashed_password:
        try:
            password_valid = verify_password(
                form_data.password, user.hashed_password)
            user_active = user.is_active
        except Exception as e:
            logger.error(f"Password verification error for user {form_data.username}: {str(e)}")
            password_valid = False
            user_active = False

    else:
        # Perform fake password check to normalize timing with proper dummy hash
        try: 
            verify_password(form_data.password, DUMMY_HASH)
        except Exception as e:
            logger.error(f"Dummy password verification error for user {form_data.username}: {str(e)}")
            pass # Ignore errors on dummy check
        password_valid = False
        user_active = False

    # Add consistent delay to prevent timing analysis
    elapsed = time.time() - start_time
    if elapsed < 0.1:  # Minimum 100ms response time
        await asyncio.sleep(0.1 - elapsed)

    # Check authentication result
    if not user or not password_valid or not user_active:
        # Log failed authentication attempt (for security monitoring)
        logger.warning(f"Failed login attempt for username: {form_data.username}")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Update last login timestamp
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Log successful login
        logger.info(f"Successful login for user: {user.username}")
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),  # Use user ID as subject (more secure)
                "username": user.username,
                "iat": int(datetime.now(timezone.utc).timestamp()),  # Issued at
                "jti": str(uuid4())  # Add unique token ID for revocation
            }
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except Exception as e:
        # Log database error but don't expose details
        logger.error(f"Database error during login for user {user.username}: {str(e)}")
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service temporarily unavailable"
        )

# Authentication router for backend docs
@router.get("/auth/verify-token")
async def verify_token_for_docs(current_user: User = Depends(get_current_user)):
    """Verify token for Nginx auth_request - admin only for docs access."""
    if not current_user.is_admin:
        logger.warning(f"Non-admin user {current_user.username} attempted to access documentation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access documentation"
        )
    
    logger.info(f"Documentation access granted to admin user: {current_user.username}")
    return {"status": "authorized", "user": current_user.username}


# Additional endpoint for token validation (optional)
@router.post("/auth/validate")
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate current token and return user info."""
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "is_active": current_user.is_active
    }


# Health check endpoint for authentication service
@router.get("/auth/health")
async def auth_health_check():
    """Health check for authentication service."""
    return {"status": "healthy", "service": "authentication"}