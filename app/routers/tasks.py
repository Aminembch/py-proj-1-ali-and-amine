"""
Task CRUD endpoints with state machine transitions.
Tasks have a strict state machine: pending -> in_progress -> blocked/done.
Real-time updates are published to Redis when task state changes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.redis_client import publish_task_update
from app.models.user import User
from app.models.task import Task
from app.models.step import Step
from app.schemas.task import TaskCreate, TaskUpdate, TaskTransition, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new task in a step.
    Initial status is always 'pending'.
    """
    # Verify step exists and user has access via workflow ownership
    step = db.query(Step).join(Step.workflow).filter(
        Step.id == task_data.step_id,
        Step.workflow.has(owner_id=current_user.id)
    ).first()
    
    if not step:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Step not found or access denied"
        )
    
    # Create task
    db_task = Task(
        step_id=task_data.step_id,
        title=task_data.title,
        description=task_data.description,
        status="pending"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Publish to Redis for real-time updates
    publish_task_update(step.workflow_id, {
        "event": "task_created",
        "task_id": db_task.id,
        "status": db_task.status,
        "title": db_task.title
    })
    
    return db_task


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    step_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all tasks.
    Optionally filter by step_id.
    Only returns tasks from workflows owned by current user.
    """
    query = db.query(Task).join(Task.step).join(Step.workflow).filter(
        Step.workflow.has(owner_id=current_user.id)
    )
    
    if step_id:
        query = query.filter(Task.step_id == step_id)
    
    tasks = query.all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific task by ID.
    """
    task = db.query(Task).join(Task.step).join(Step.workflow).filter(
        Task.id == task_id,
        Step.workflow.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update task title or description.
    Does not change status - use /tasks/{id}/transition for that.
    """
    task = db.query(Task).join(Task.step).join(Step.workflow).filter(
        Task.id == task_id,
        Step.workflow.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    
    db.commit()
    db.refresh(task)
    return task


@router.post("/{task_id}/transition", response_model=TaskResponse)
def transition_task(
    task_id: int,
    transition_data: TaskTransition,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Transition a task to a new state.
    
    State machine rules:
    - pending -> in_progress
    - in_progress -> blocked | done
    - blocked -> in_progress
    - done is terminal (no transitions allowed)
    
    Publishes update to Redis for WebSocket clients.
    """
    task = db.query(Task).join(Task.step).join(Step.workflow).filter(
        Task.id == task_id,
        Step.workflow.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Attempt transition using state machine
    if not task.transition_to(transition_data.desired_state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{task.status}' to '{transition_data.desired_state}'"
        )
    
    db.commit()
    db.refresh(task)
    
    # Get workflow_id for Redis channel
    workflow_id = task.step.workflow_id
    
    # Publish to Redis for real-time updates
    publish_task_update(workflow_id, {
        "event": "task_updated",
        "task_id": task.id,
        "status": task.status,
        "title": task.title
    })
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task.
    """
    task = db.query(Task).join(Task.step).join(Step.workflow).filter(
        Task.id == task_id,
        Step.workflow.has(owner_id=current_user.id)
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    workflow_id = task.step.workflow_id
    
    db.delete(task)
    db.commit()
    
    # Publish deletion event
    publish_task_update(workflow_id, {
        "event": "task_deleted",
        "task_id": task_id
    })
    
    return None
