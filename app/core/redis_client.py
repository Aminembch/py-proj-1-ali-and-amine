"""
Redis client setup for pub/sub and caching.
We use Redis for real-time WebSocket broadcasting and background task coordination.
"""
import redis
from app.core.config import settings

# Create Redis connection pool (reused across requests for efficiency)
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis():
    """
    Dependency function that returns the Redis client.
    Usage: def endpoint(redis_conn = Depends(get_redis))
    """
    return redis_client


# Pub/Sub channels
TASK_UPDATE_CHANNEL = "task_updates:{workflow_id}"


def publish_task_update(workflow_id: int, message: dict):
    """
    Publish a task update to the workflow-specific Redis channel.
    All WebSocket clients subscribed to this workflow will receive the message.
    """
    channel = TASK_UPDATE_CHANNEL.format(workflow_id=workflow_id)
    # Redis pub/sub requires string messages, so we'll send JSON
    import json
    redis_client.publish(channel, json.dumps(message))
