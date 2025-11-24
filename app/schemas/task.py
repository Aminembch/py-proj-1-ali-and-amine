"""
Pydantic schemas for Task-related requests and responses.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    step_id: int
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None


class TaskTransition(BaseModel):
    """Schema for transitioning task state."""
    desired_state: str


class TaskResponse(BaseModel):
    """Schema for task data in responses."""
    id: int
    step_id: int
    title: str
    description: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class TaskWithStep(TaskResponse):
    """Extended task response with step information."""
    step_name: str
    workflow_id: int
