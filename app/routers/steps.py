"""
Step CRUD endpoints (nested under workflows).
Steps belong to a workflow and are ordered.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workflow import Workflow
from app.models.step import Step
from app.schemas.step import StepCreate, StepUpdate, StepResponse

router = APIRouter(prefix="/workflows/{workflow_id}/steps", tags=["steps"])


def verify_workflow_access(workflow_id: int, db: Session, current_user: User) -> Workflow:
    """
    Helper function to verify user has access to workflow.
    Returns the workflow if found, raises HTTPException otherwise.
    """
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.post("/", response_model=StepResponse, status_code=status.HTTP_201_CREATED)
def create_step(
    workflow_id: int,
    step_data: StepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new step in a workflow.
    """
    # Verify workflow access
    verify_workflow_access(workflow_id, db, current_user)
    
    # Create step
    db_step = Step(
        workflow_id=workflow_id,
        name=step_data.name,
        order=step_data.order,
        expected_duration_hours=step_data.expected_duration_hours,
        assigned_user_id=step_data.assigned_user_id
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step


@router.get("/", response_model=List[StepResponse])
def list_steps(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all steps in a workflow, ordered by the 'order' field.
    """
    # Verify workflow access
    verify_workflow_access(workflow_id, db, current_user)
    
    # Get steps ordered by order field
    steps = db.query(Step).filter(
        Step.workflow_id == workflow_id
    ).order_by(Step.order).all()
    
    return steps


@router.get("/{step_id}", response_model=StepResponse)
def get_step(
    workflow_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific step by ID.
    """
    # Verify workflow access
    verify_workflow_access(workflow_id, db, current_user)
    
    step = db.query(Step).filter(
        Step.id == step_id,
        Step.workflow_id == workflow_id
    ).first()
    
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )
    
    return step


@router.put("/{step_id}", response_model=StepResponse)
def update_step(
    workflow_id: int,
    step_id: int,
    step_data: StepUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a step's properties.
    """
    # Verify workflow access
    verify_workflow_access(workflow_id, db, current_user)
    
    step = db.query(Step).filter(
        Step.id == step_id,
        Step.workflow_id == workflow_id
    ).first()
    
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )
    
    # Update fields if provided
    if step_data.name is not None:
        step.name = step_data.name
    if step_data.order is not None:
        step.order = step_data.order
    if step_data.expected_duration_hours is not None:
        step.expected_duration_hours = step_data.expected_duration_hours
    if step_data.assigned_user_id is not None:
        step.assigned_user_id = step_data.assigned_user_id
    
    db.commit()
    db.refresh(step)
    return step


@router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step(
    workflow_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a step.
    Cascade deletion will remove all tasks in this step.
    """
    # Verify workflow access
    verify_workflow_access(workflow_id, db, current_user)
    
    step = db.query(Step).filter(
        Step.id == step_id,
        Step.workflow_id == workflow_id
    ).first()
    
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found"
        )
    
    db.delete(step)
    db.commit()
    return None
