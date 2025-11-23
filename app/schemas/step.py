"""
Pydantic schemas for Step-related requests and responses.
"""
from pydantic import BaseModel
from typing import Optional


class StepCreate(BaseModel):
    """Schema for creating a new step."""
    name: str
    order: int
    expected_duration_hours: float = 0.0
    assigned_user_id: Optional[int] = None


class StepUpdate(BaseModel):
    """Schema for updating a step."""
    name: Optional[str] = None
    order: Optional[int] = None
    expected_duration_hours: Optional[float] = None
    assigned_user_id: Optional[int] = None


class StepResponse(BaseModel):
    """Schema for step data in responses."""
    id: int
    workflow_id: int
    name: str
    order: int
    expected_duration_hours: float
    assigned_user_id: Optional[int] = None
    
    class Config:
        from_attributes = True
