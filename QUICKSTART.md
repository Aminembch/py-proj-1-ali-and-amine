# Smart Workflow Assistant - Quick Start Guide

Get the backend running in 5 minutes!

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Git

## Step 1: Start Databases (30 seconds)

```bash
docker-compose up -d
```

This starts PostgreSQL and Redis in the background.

## Step 2: Setup Environment (2 minutes)

```bash
# Run automated setup
./setup.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Copy .env.example to .env
- Run database migrations

**Or do it manually:**

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run migrations
alembic upgrade head
```

## Step 3: Start the Server (10 seconds)

```bash
./run_server.sh
```

**Or manually:**

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

The API is now running at http://localhost:8000

## Step 4: Explore the API

Open http://localhost:8000/docs in your browser for interactive API documentation.

## Step 5: Run Tests (30 seconds)

```bash
pytest
```

You should see: **20 passed**

## Step 6: Try the API (optional)

Run the automated test script:

```bash
./test_api_manual.sh
```

This will:
- Register a user
- Create a workflow
- Add steps
- Create and transition tasks
- Show analytics

## Optional: Start Background Worker

In a new terminal:

```bash
./run_worker.sh
```

This checks for overdue tasks every 60 seconds.

## What's Next?

### Explore the Code

- `app/main.py` - FastAPI application
- `app/models/` - Database models
- `app/routers/` - API endpoints
- `tests/` - Test suite

### Read the Documentation

- `README_BACKEND.md` - Complete user guide with curl examples
- `IMPLEMENTATION_NOTES.md` - Design decisions and teaching notes

### Connect a Frontend

The API is ready for a React/Vue/Angular frontend:
- CORS is configured
- JWT authentication works
- WebSocket endpoint available at `ws://localhost:8000/ws/workflow/{id}?token={jwt}`

### Deploy to Production

See the deployment checklist in `IMPLEMENTATION_NOTES.md`

## Common Issues

### Port 8000 already in use

```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### PostgreSQL connection refused

```bash
# Check Docker is running
docker-compose ps

# Restart services
docker-compose restart
```

### Tests fail

```bash
# Clean test database
rm -f test.db

# Run tests again
pytest
```

### Dependencies won't install

```bash
# Upgrade pip
pip install --upgrade pip

# Install again
pip install -r requirements.txt
```

## Architecture Overview

```
Client Request → FastAPI → Router → Database/Redis → Response
                    ↓
                WebSocket → Redis Pub/Sub → All Connected Clients
                    ↓
             Background Worker → Checks Tasks → Sends Alerts
```

## API Endpoints Summary

### Authentication
- POST `/register` - Create new user
- POST `/login` - Get JWT token

### Workflows
- POST `/workflows/` - Create workflow
- GET `/workflows/` - List workflows
- GET `/workflows/{id}` - Get workflow
- PUT `/workflows/{id}` - Update workflow
- DELETE `/workflows/{id}` - Delete workflow

### Steps (nested under workflows)
- POST `/workflows/{id}/steps/` - Create step
- GET `/workflows/{id}/steps/` - List steps
- GET `/workflows/{id}/steps/{step_id}` - Get step
- PUT `/workflows/{id}/steps/{step_id}` - Update step
- DELETE `/workflows/{id}/steps/{step_id}` - Delete step

### Tasks
- POST `/tasks/` - Create task
- GET `/tasks/` - List tasks
- GET `/tasks/{id}` - Get task
- PUT `/tasks/{id}` - Update task
- POST `/tasks/{id}/transition` - Change task state
- DELETE `/tasks/{id}` - Delete task

### Analytics
- GET `/analytics/workflow/{id}/bottlenecks` - Get workflow metrics

### Real-time
- WebSocket `/ws/workflow/{id}?token={jwt}` - Real-time updates

## State Machine

Tasks follow strict state transitions:

```
pending → in_progress → done
            ↓
          blocked → in_progress
```

Invalid transitions return 400 Bad Request.

## Technology Stack

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database
- **PostgreSQL** - Relational database
- **Redis** - Real-time pub/sub
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **JWT** - Authentication
- **pytest** - Testing framework

## Support

Questions? Check:
1. `README_BACKEND.md` for detailed documentation
2. `IMPLEMENTATION_NOTES.md` for design explanations
3. http://localhost:8000/docs for API reference
4. GitHub Issues for bug reports

## License

See LICENSE file for details.

---

**Happy coding! 🚀**
