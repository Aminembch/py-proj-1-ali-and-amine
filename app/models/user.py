"""
User model for authentication and authorization.
Stores user credentials and role (admin/user).
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """
    User table stores authentication information.
    
    Fields:
        id: Primary key
        email: Unique user email (used for login)
        hashed_password: Bcrypt hashed password
        role: Either "admin" or "user" (for authorization)
        created_at: Account creation timestamp
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # "admin" or "user"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    workflows = relationship("Workflow", back_populates="owner", cascade="all, delete-orphan")
    assigned_steps = relationship("Step", back_populates="assigned_user")
