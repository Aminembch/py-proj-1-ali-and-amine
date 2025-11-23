"""
Pydantic schemas for Workflow-related requests and responses.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WorkflowCreate(BaseModel):
    """Schema for creating a new workflow."""
    name: str


class WorkflowUpdate(BaseModel):
    """Schema for updating a workflow."""
    name: Optional[str] = None


class WorkflowResponse(BaseModel):
    """Schema for workflow data in responses."""
    id: int
    name: str
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
