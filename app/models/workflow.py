"""
Workflow model represents a collection of steps.
Each workflow is owned by a user and contains multiple steps.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Workflow(Base):
    """
    Workflow table stores workflow definitions.
    
    Fields:
        id: Primary key
        name: Workflow name/title
        owner_id: Foreign key to User who created this workflow
        created_at: Workflow creation timestamp
    """
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="workflows")
    steps = relationship("Step", back_populates="workflow", cascade="all, delete-orphan")
