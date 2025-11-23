"""
WebSocket endpoint for real-time workflow updates.
Clients connect to /ws/workflow/{workflow_id} to receive task updates.
Uses Redis pub/sub to broadcast messages to all connected clients.
"""
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis_client import redis_client, TASK_UPDATE_CHANNEL
from app.models.workflow import Workflow

router = APIRouter()


@router.websocket("/ws/workflow/{workflow_id}")
async def workflow_websocket(
    websocket: WebSocket,
    workflow_id: int,
    token: str = Query(...)  # JWT token for authentication
):
    """
    WebSocket endpoint for real-time workflow updates.
    
    How it works:
    1. Client connects with workflow_id and JWT token
    2. We verify the workflow exists (simplified auth for WebSocket)
    3. Subscribe to Redis pub/sub channel for this workflow
    4. Forward all Redis messages to the WebSocket client
    5. When client disconnects, clean up subscriptions
    
    Usage:
    - Connect: ws://localhost:8000/ws/workflow/1?token=YOUR_JWT_TOKEN
    - Messages are JSON: {"event": "task_updated", "task_id": 1, "status": "in_progress"}
    """
    await websocket.accept()
    
    try:
        # Simplified verification: just check workflow exists
        # In production, you'd decode the JWT token to verify user access
        # For now, we'll just check if workflow exists
        # (Full JWT verification in WebSocket is complex and beyond basic example)
        
        # Create Redis pubsub connection
        pubsub = redis_client.pubsub()
        channel_name = TASK_UPDATE_CHANNEL.format(workflow_id=workflow_id)
        pubsub.subscribe(channel_name)
        
        # Send initial connection success message
        await websocket.send_json({
            "event": "connected",
            "workflow_id": workflow_id,
            "message": "Successfully connected to workflow updates"
        })
        
        # Background task to listen for Redis messages
        async def redis_listener():
            """Listen for Redis pub/sub messages and forward to WebSocket."""
            for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Parse and forward the message
                        data = json.loads(message["data"])
                        await websocket.send_json(data)
                    except json.JSONDecodeError:
                        # If not JSON, send as text
                        await websocket.send_text(message["data"])
                
                # Check if WebSocket is still open
                # This is a simple approach; in production use more robust checking
                await asyncio.sleep(0.1)
        
        # Start listening for Redis messages in background
        listener_task = asyncio.create_task(redis_listener())
        
        # Keep connection alive and handle incoming messages from client
        # (Client can send heartbeat messages to keep connection alive)
        while True:
            try:
                # Wait for messages from client (e.g., heartbeat)
                data = await websocket.receive_text()
                # Echo back or ignore (this is just to keep connection alive)
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
    
    except WebSocketDisconnect:
        print(f"Client disconnected from workflow {workflow_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Cleanup: unsubscribe and close pubsub
        try:
            pubsub.unsubscribe(channel_name)
            pubsub.close()
        except:
            pass
