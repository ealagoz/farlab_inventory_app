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
from utils.security import verify_password, create_access_token
from schemas.token import Token

# Create a new router
router = APIRouter(
    prefix="",
    tags=["Authentication"]
)


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
    if user:
        password_valid = verify_password(
            form_data.password, user.hashed_password)
        user_active = user.is_active

    else:
        # Perform fake password check to normalize timing
        verify_password(form_data.password,
                        "$2b$12$dummy.hash.to.prevent.timing.attacks")
        password_valid = False
        user_active = False

    # Add consistent delay to prevent timing analysis
    elapsed = time.time() - start_time
    if elapsed < 0.1:  # Minimum 100ms response time
        await asyncio.sleep(0.1 - elapsed)

    if not user or not password_valid or not user_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    access_token = create_access_token(
        data={"sub": str(user.id),  # Use user ID as subject (more secure)
              "username": user.username,
              # Issued at (iat)
              "iat": int(datetime.now(timezone.utc).timestamp()),
              "jti": str(uuid4())  # Add unique token ID for revocation
              }
    )

    return {"access_token": access_token, "token_type": "bearer"}
