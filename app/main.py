"""
Main FastAPI application.
This sets up the FastAPI app, registers all routers, and configures CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, workflows, steps, tasks, analytics, websocket

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


@app.on_event("startup")
async def startup_event():
    """
    Create database tables on startup.
    In production, use Alembic migrations instead.
    """
    # Import here to avoid circular imports
    from app.core.database import engine, Base
    Base.metadata.create_all(bind=engine)


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
