from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


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


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8,
                          description="User password (min 8 characters long)")


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
                              description="New password (min 8 characters long)")
