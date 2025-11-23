"""
Main FastAPI application.
This sets up the FastAPI app, registers all routers, and configures CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from app.routers import auth, workflows, steps, tasks, analytics, websocket

# Initialize FastAPI app
app = FastAPI(
    title="Smart Workflow Assistant API",
    description="Backend API for workflow automation with real-time updates",
    version="1.0.0"
)

# Mount static files directory (for the landing page)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # If database connection fails, log but don't crash
        # This allows the landing page to still be accessible
        print(f"Warning: Could not connect to database: {e}")
        print("The API landing page is still accessible, but API endpoints will not work until database is connected.")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Root endpoint - serves landing page with API information.
    """
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    
    # If HTML file exists, serve it
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    
    # Fallback to JSON response if HTML not found
    return """
    <html>
        <body>
            <h1>Smart Workflow Assistant API</h1>
            <p>API is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """


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
