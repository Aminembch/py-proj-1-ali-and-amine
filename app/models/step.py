"""
Step model represents a stage in a workflow.
Steps are ordered and have expected durations for analytics.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Step(Base):
    """
    Step table stores workflow steps.
    
    Fields:
        id: Primary key
        workflow_id: Foreign key to parent Workflow
        name: Step name/title
        order: Step order in the workflow (for sequencing)
        expected_duration_hours: Expected time to complete (for bottleneck analysis)
        assigned_user_id: Optional user assigned to this step
    """
    __tablename__ = "steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    expected_duration_hours = Column(Float, default=0.0, nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="steps")
    assigned_user = relationship("User", back_populates="assigned_steps")
    tasks = relationship("Task", back_populates="step", cascade="all, delete-orphan")
