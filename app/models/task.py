"""
Task model represents individual work items within a step.
Tasks have a state machine with specific allowed transitions.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class Task(Base):
    """
    Task table stores individual tasks within workflow steps.
    
    Fields:
        id: Primary key
        step_id: Foreign key to parent Step
        title: Task title
        description: Detailed task description
        status: Current task status (state machine: pending/in_progress/blocked/done)
        started_at: When the task was started (moved to in_progress)
        completed_at: When the task was completed (moved to done)
    
    State Machine:
        pending -> in_progress
        in_progress -> blocked | done
        blocked -> in_progress
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("steps.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending", nullable=False)  # pending, in_progress, blocked, done
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    step = relationship("Step", back_populates="tasks")
    
    # State machine definition
    ALLOWED_TRANSITIONS = {
        "pending": ["in_progress"],
        "in_progress": ["blocked", "done"],
        "blocked": ["in_progress"],
        "done": []  # Terminal state
    }
    
    def can_transition_to(self, new_status: str) -> bool:
        """
        Check if transition from current status to new_status is allowed.
        
        Returns:
            True if transition is valid, False otherwise
        """
        return new_status in self.ALLOWED_TRANSITIONS.get(self.status, [])
    
    def transition_to(self, new_status: str) -> bool:
        """
        Attempt to transition to a new status.
        Updates timestamps automatically.
        
        Returns:
            True if transition succeeded, False if not allowed
        """
        if not self.can_transition_to(new_status):
            return False
        
        # Update timestamps based on transitions
        if new_status == "in_progress" and self.status == "pending":
            self.started_at = datetime.utcnow()
        elif new_status == "done":
            self.completed_at = datetime.utcnow()
        
        self.status = new_status
        return True
