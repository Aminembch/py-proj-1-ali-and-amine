"""
Pydantic schemas for User-related requests and responses.
These validate incoming data and serialize outgoing data.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """Schema for user registration request."""
    email: EmailStr
    password: str
    role: Optional[str] = "user"  # Default to regular user


class UserLogin(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user data in responses (no password)."""
    id: int
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows converting SQLAlchemy models to Pydantic


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
