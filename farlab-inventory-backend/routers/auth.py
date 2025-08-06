# /auth/login and /auth/register endpoints
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from database import get_db
from models.user import User
from utils.security import verify_password, create_access_token
from schemas.token import Token

# Create a new router
router = APIRouter(
    prefix="/api",
    tags=["Authentication"]
)


@router.post("/token", response_model=Token, name="token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """Authenticate user and return a JWT access token."""
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "username": user.username}
    )

    return {"access_token": access_token, "token_type": "bearer"}
