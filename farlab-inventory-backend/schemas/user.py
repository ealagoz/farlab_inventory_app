from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re


class UserBase(BaseModel):
    """Base schema for user data."""
    username: str = Field(..., min_length=3, max_length=50,
                          description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1,
                            max_length=50, description="First name")
    last_name: str = Field(..., min_length=1,
                           max_length=50, description="Last name")
    phone: Optional[str] = Field(
        None, max_length=20, description="Phone number")
    department: Optional[str] = Field(
        None, max_length=100, description="Department")
    position: Optional[str] = Field(
        None, max_length=100, description="Position/Role")
    notes: Optional[str] = Field(None, description="Additional notes")


def validate_password_strength(password: str) -> List[str]:
    """Validate password meets security requirements."""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     errors.append("Password must contain at least one special character")

    # Check for common passwords
    common_passwords = {"password123", "admin123", "123456789", "qwerty123"}
    if password.lower() in common_passwords:
        errors.append("Password is to common")

    return errors


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8,
                          description="User password")

    @field_validator('password')
    def validate_password(cls, v):
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response (excludes password)."""
    id: int
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class PasswordChange(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(...,
                              description="New password")

    @field_validator('new_password')
    def validate_new_password(cls, v):
        errors = validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v
