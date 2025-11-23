"""
Main FastAPI application.
This sets up the FastAPI app, registers all routers, and configures CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, workflows, steps, tasks, analytics, websocket
from app.core.database import engine, Base

# Create all database tables
# In production, you'd use Alembic migrations instead
# But this ensures tables exist on startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Workflow Assistant API",
    description="Backend API for workflow automation with real-time updates",
    version="1.0.0"
)

# Configure CORS (allow frontend to access API)
# In production, restrict origins to your actual frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
# Auth endpoints (no prefix, directly at /register and /login)
app.include_router(auth.router, tags=["auth"])

# Main API routers
app.include_router(workflows.router)
app.include_router(steps.router)
app.include_router(tasks.router)
app.include_router(analytics.router)

# WebSocket router
app.include_router(websocket.router)


@app.get("/")
def read_root():
    """
    Root endpoint - simple health check.
    """
    return {
        "message": "Smart Workflow Assistant API",
        "status": "running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Run with: python -m app.main
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
