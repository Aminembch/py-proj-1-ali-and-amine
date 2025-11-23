"""
Unit tests for the Task state machine.
These tests verify that state transitions follow the defined rules.

State machine rules:
- pending -> in_progress
- in_progress -> blocked | done
- blocked -> in_progress
- done is terminal (no transitions allowed)
"""
import pytest
from datetime import datetime

from app.models.task import Task


def test_pending_to_in_progress():
    """Test valid transition from pending to in_progress."""
    task = Task(status="pending", title="Test Task")
    
    # Should be able to transition
    assert task.can_transition_to("in_progress")
    
    # Perform transition
    result = task.transition_to("in_progress")
    assert result is True
    assert task.status == "in_progress"
    assert task.started_at is not None  # Timestamp should be set


def test_pending_to_blocked_invalid():
    """Test invalid transition from pending to blocked."""
    task = Task(status="pending", title="Test Task")
    
    # Should NOT be able to transition directly to blocked
    assert not task.can_transition_to("blocked")
    
    # Attempt transition should fail
    result = task.transition_to("blocked")
    assert result is False
    assert task.status == "pending"  # Status unchanged


def test_pending_to_done_invalid():
    """Test invalid transition from pending to done."""
    task = Task(status="pending", title="Test Task")
    
    # Should NOT be able to transition directly to done
    assert not task.can_transition_to("done")
    
    result = task.transition_to("done")
    assert result is False
    assert task.status == "pending"


def test_in_progress_to_blocked():
    """Test valid transition from in_progress to blocked."""
    task = Task(status="in_progress", title="Test Task")
    
    assert task.can_transition_to("blocked")
    
    result = task.transition_to("blocked")
    assert result is True
    assert task.status == "blocked"


def test_in_progress_to_done():
    """Test valid transition from in_progress to done."""
    task = Task(status="in_progress", title="Test Task")
    
    assert task.can_transition_to("done")
    
    result = task.transition_to("done")
    assert result is True
    assert task.status == "done"
    assert task.completed_at is not None  # Timestamp should be set


def test_in_progress_to_pending_invalid():
    """Test invalid transition from in_progress back to pending."""
    task = Task(status="in_progress", title="Test Task")
    
    # Cannot go back to pending
    assert not task.can_transition_to("pending")
    
    result = task.transition_to("pending")
    assert result is False
    assert task.status == "in_progress"


def test_blocked_to_in_progress():
    """Test valid transition from blocked to in_progress."""
    task = Task(status="blocked", title="Test Task")
    
    assert task.can_transition_to("in_progress")
    
    result = task.transition_to("in_progress")
    assert result is True
    assert task.status == "in_progress"


def test_blocked_to_done_invalid():
    """Test invalid transition from blocked to done."""
    task = Task(status="blocked", title="Test Task")
    
    # Must go through in_progress first
    assert not task.can_transition_to("done")
    
    result = task.transition_to("done")
    assert result is False
    assert task.status == "blocked"


def test_done_is_terminal():
    """Test that done status is terminal - no transitions allowed."""
    task = Task(status="done", title="Test Task")
    
    # Cannot transition to any state from done
    assert not task.can_transition_to("pending")
    assert not task.can_transition_to("in_progress")
    assert not task.can_transition_to("blocked")
    assert not task.can_transition_to("done")
    
    # All transition attempts should fail
    assert task.transition_to("pending") is False
    assert task.transition_to("in_progress") is False
    assert task.transition_to("blocked") is False
    assert task.status == "done"


def test_full_workflow_happy_path():
    """Test a complete workflow: pending -> in_progress -> done."""
    task = Task(status="pending", title="Complete Task")
    
    # Step 1: Start the task
    assert task.transition_to("in_progress")
    assert task.status == "in_progress"
    assert task.started_at is not None
    started_time = task.started_at
    
    # Step 2: Complete the task
    assert task.transition_to("done")
    assert task.status == "done"
    assert task.completed_at is not None
    assert task.started_at == started_time  # Started time unchanged


def test_blocked_workflow():
    """Test workflow with blocking: pending -> in_progress -> blocked -> in_progress -> done."""
    task = Task(status="pending", title="Blocked Task")
    
    # Start
    assert task.transition_to("in_progress")
    
    # Get blocked
    assert task.transition_to("blocked")
    assert task.status == "blocked"
    
    # Resume
    assert task.transition_to("in_progress")
    assert task.status == "in_progress"
    
    # Complete
    assert task.transition_to("done")
    assert task.status == "done"
