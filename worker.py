"""
Background worker for checking task alerts.
This worker runs periodically to check for overdue tasks and send alerts.

Design choice:
- Using a simple infinite loop with sleep (instead of Celery/RQ)
- This is the simplest approach that works locally without extra setup
- For production, consider using APScheduler, Celery, or RQ for more features

How it works:
1. Every N seconds, query database for tasks that are overdue
2. For each overdue task, send an alert (log + Redis publish + email stub)
3. Track which tasks have been alerted to avoid duplicate alerts
"""
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.redis_client import publish_task_update, redis_client
from app.models.task import Task
from app.models.step import Step
from app.utils.email import send_alert_email

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check interval in seconds
CHECK_INTERVAL = 60  # Check every 60 seconds

# Redis key for tracking alerted tasks
ALERTED_TASKS_KEY = "alerted_tasks"


def check_overdue_tasks():
    """
    Check for tasks that have exceeded their expected duration.
    Send alerts for overdue tasks that haven't been alerted yet.
    """
    db: Session = SessionLocal()
    
    try:
        # Get all in_progress tasks with their steps
        tasks = db.query(Task).join(Task.step).filter(
            Task.status == "in_progress",
            Task.started_at.isnot(None)
        ).all()
        
        current_time = datetime.utcnow()
        
        for task in tasks:
            step = task.step
            
            # Skip if no expected duration set
            if step.expected_duration_hours <= 0:
                continue
            
            # Calculate elapsed time
            elapsed = current_time - task.started_at
            elapsed_hours = elapsed.total_seconds() / 3600
            
            # Check if task is overdue
            if elapsed_hours > step.expected_duration_hours:
                # Check if we've already alerted for this task
                task_key = f"task:{task.id}"
                if redis_client.sismember(ALERTED_TASKS_KEY, task_key):
                    # Already alerted, skip
                    continue
                
                # Mark as alerted
                redis_client.sadd(ALERTED_TASKS_KEY, task_key)
                
                # Log alert
                logger.warning(
                    f"ALERT: Task #{task.id} '{task.title}' is overdue! "
                    f"Expected: {step.expected_duration_hours}h, "
                    f"Actual: {elapsed_hours:.2f}h"
                )
                
                # Publish to Redis for real-time notification
                workflow_id = step.workflow_id
                publish_task_update(workflow_id, {
                    "event": "task_overdue_alert",
                    "task_id": task.id,
                    "task_title": task.title,
                    "step_name": step.name,
                    "expected_hours": step.expected_duration_hours,
                    "elapsed_hours": round(elapsed_hours, 2),
                    "message": f"Task '{task.title}' is overdue by {elapsed_hours - step.expected_duration_hours:.1f} hours"
                })
                
                # Send email alert (stub)
                workflow = step.workflow
                owner_email = workflow.owner.email
                
                email_subject = f"Alert: Task Overdue - {task.title}"
                email_body = f"""
Task Alert - Overdue Task Detected

Workflow: {workflow.name}
Step: {step.name}
Task: {task.title}

Expected Duration: {step.expected_duration_hours} hours
Actual Duration: {elapsed_hours:.2f} hours
Overdue By: {elapsed_hours - step.expected_duration_hours:.2f} hours

Please take action on this task.

Started At: {task.started_at}
Current Time: {current_time}
                """
                
                send_alert_email([owner_email], email_subject, email_body)
        
        logger.info(f"Checked {len(tasks)} in-progress tasks for alerts")
    
    except Exception as e:
        logger.error(f"Error checking overdue tasks: {e}")
    finally:
        db.close()


def run_worker():
    """
    Main worker loop.
    Runs indefinitely, checking for overdue tasks at regular intervals.
    """
    logger.info("Starting background worker for task alerts...")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    
    while True:
        try:
            check_overdue_tasks()
        except Exception as e:
            logger.error(f"Worker error: {e}")
        
        # Sleep until next check
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_worker()
