"""
Analytics endpoints for workflow performance analysis.
Provides bottleneck detection and metrics.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workflow import Workflow
from app.models.step import Step
from app.models.task import Task

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/workflow/{workflow_id}/bottlenecks")
def get_workflow_bottlenecks(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Analyze workflow bottlenecks.
    
    Returns:
    - Average time per step (for completed tasks)
    - Number of tasks pending/in_progress/blocked per step
    - Steps that exceed expected duration
    
    This helps identify which steps are taking longer than expected
    or have too many blocked/pending tasks.
    """
    # Verify workflow access
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Get all steps with their tasks
    steps = db.query(Step).filter(Step.workflow_id == workflow_id).all()
    
    bottlenecks = []
    
    for step in steps:
        # Count tasks by status
        status_counts = db.query(Task.status, func.count(Task.id)).filter(
            Task.step_id == step.id
        ).group_by(Task.status).all()
        
        status_dict = {status: count for status, count in status_counts}
        
        # Calculate average completion time for done tasks
        completed_tasks = db.query(Task).filter(
            Task.step_id == step.id,
            Task.status == "done",
            Task.started_at.isnot(None),
            Task.completed_at.isnot(None)
        ).all()
        
        avg_hours = None
        if completed_tasks:
            total_hours = 0
            for task in completed_tasks:
                duration = (task.completed_at - task.started_at).total_seconds() / 3600
                total_hours += duration
            avg_hours = total_hours / len(completed_tasks)
        
        # Determine if this is a bottleneck
        is_bottleneck = False
        bottleneck_reason = []
        
        if avg_hours and step.expected_duration_hours > 0:
            if avg_hours > step.expected_duration_hours:
                is_bottleneck = True
                bottleneck_reason.append(f"Avg time ({avg_hours:.1f}h) exceeds expected ({step.expected_duration_hours}h)")
        
        if status_dict.get("blocked", 0) > 0:
            is_bottleneck = True
            bottleneck_reason.append(f"{status_dict['blocked']} blocked tasks")
        
        if status_dict.get("pending", 0) > 3:  # Arbitrary threshold
            is_bottleneck = True
            bottleneck_reason.append(f"{status_dict['pending']} pending tasks")
        
        bottlenecks.append({
            "step_id": step.id,
            "step_name": step.name,
            "order": step.order,
            "expected_duration_hours": step.expected_duration_hours,
            "avg_actual_duration_hours": round(avg_hours, 2) if avg_hours else None,
            "tasks_pending": status_dict.get("pending", 0),
            "tasks_in_progress": status_dict.get("in_progress", 0),
            "tasks_blocked": status_dict.get("blocked", 0),
            "tasks_done": status_dict.get("done", 0),
            "is_bottleneck": is_bottleneck,
            "bottleneck_reasons": bottleneck_reason
        })
    
    return {
        "workflow_id": workflow_id,
        "workflow_name": workflow.name,
        "steps": bottlenecks,
        "total_steps": len(steps)
    }
