# Smart Workflow Assistant - Python Backend

A FastAPI-based backend for workflow automation with real-time updates, state machines, and analytics.

## Architecture Overview

This backend implements:
- **FastAPI** for HTTP endpoints and WebSockets
- **SQLAlchemy ORM** with Alembic migrations for PostgreSQL
- **Redis** for pub/sub (real-time updates) and background task coordination
- **JWT authentication** with role-based access control
- **State machine** for task transitions
- **Background worker** for overdue task alerts
- **Comprehensive tests** with pytest

## Prerequisites

- Python 3.9+
- Docker and Docker Compose (for PostgreSQL and Redis)
- pip (Python package manager)

## Quick Start

### 1. Start PostgreSQL and Redis

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on port 5432
- Redis on port 6379

Check they're running:
```bash
docker-compose ps
```

### 2. Set up Python environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (defaults work for local development)
```

Default `.env` values:
```env
DATABASE_URL=postgresql://workflow_user:workflow_pass@localhost:5432/workflow_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Change `SECRET_KEY` in production!

### 4. Run database migrations

```bash
# Initialize Alembic (creates migration table)
alembic upgrade head
```

If you make model changes, create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

### 5. Start the FastAPI server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is now running at http://localhost:8000
- API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### 6. Start the background worker (in a new terminal)

```bash
# Activate venv first
source venv/bin/activate

# Run worker
python worker.py
```

The worker checks for overdue tasks every 60 seconds and sends alerts.

## Testing

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_state_machine.py
pytest tests/test_api.py
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## API Usage Examples

### 1. Register a user

```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "role": "user"
  }'
```

### 2. Login (get JWT token)

```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

Save the `access_token` from the response. Use it in subsequent requests.

### 3. Create a workflow

```bash
TOKEN="your_access_token_here"

curl -X POST "http://localhost:8000/workflows/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Workflow"
  }'
```

Save the `id` from the response (e.g., workflow_id=1).

### 4. Create steps in the workflow

```bash
WORKFLOW_ID=1

# Step 1
curl -X POST "http://localhost:8000/workflows/$WORKFLOW_ID/steps/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Planning",
    "order": 1,
    "expected_duration_hours": 2.0
  }'

# Step 2
curl -X POST "http://localhost:8000/workflows/$WORKFLOW_ID/steps/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Development",
    "order": 2,
    "expected_duration_hours": 8.0
  }'
```

Save the `id` from each step (e.g., step_id=1, step_id=2).

### 5. Create a task

```bash
STEP_ID=1

curl -X POST "http://localhost:8000/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "step_id": '$STEP_ID',
    "title": "Define requirements",
    "description": "Gather and document all requirements"
  }'
```

Save the `id` from the response (e.g., task_id=1).

### 6. Transition task state

```bash
TASK_ID=1

# Start the task (pending -> in_progress)
curl -X POST "http://localhost:8000/tasks/$TASK_ID/transition" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_state": "in_progress"
  }'

# Complete the task (in_progress -> done)
curl -X POST "http://localhost:8000/tasks/$TASK_ID/transition" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_state": "done"
  }'

# Block a task (in_progress -> blocked)
curl -X POST "http://localhost:8000/tasks/$TASK_ID/transition" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_state": "blocked"
  }'
```

### 7. Get workflow analytics

```bash
curl -X GET "http://localhost:8000/analytics/workflow/$WORKFLOW_ID/bottlenecks" \
  -H "Authorization: Bearer $TOKEN"
```

This returns metrics about each step:
- Average completion time
- Task counts by status
- Bottleneck detection

## WebSocket Usage

Connect to real-time updates for a workflow:

```javascript
// JavaScript example
const ws = new WebSocket('ws://localhost:8000/ws/workflow/1?token=YOUR_JWT_TOKEN');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received update:', data);
  // Handle different event types:
  // - task_created
  // - task_updated
  // - task_deleted
  // - task_overdue_alert
};

ws.onopen = () => {
  console.log('Connected to workflow updates');
  // Send heartbeat to keep connection alive
  setInterval(() => ws.send('ping'), 30000);
};
```

Using `websocat` (command line tool):
```bash
websocat "ws://localhost:8000/ws/workflow/1?token=$TOKEN"
```

## State Machine Rules

Task status transitions follow strict rules:

```
pending → in_progress
    ↓
in_progress → blocked | done
    ↓
blocked → in_progress
    
done (terminal - no transitions)
```

Invalid transitions will return 400 Bad Request.

## Background Worker Alerts

The worker (`worker.py`) checks for overdue tasks every 60 seconds.

**How it works:**
1. Finds all tasks in "in_progress" status
2. Compares elapsed time against step's `expected_duration_hours`
3. If overdue, sends alerts:
   - Logs a warning
   - Publishes to Redis (WebSocket clients receive notification)
   - Calls email stub (logs email details)

**Configuring email (production):**

Edit `app/utils/email.py` to enable real email sending:

1. Uncomment the SMTP code
2. Set environment variables:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM=your-email@gmail.com
   ```

For SendGrid or other services, install the SDK and replace the SMTP code.

## Project Structure

```
.
├── app/
│   ├── core/           # Configuration, database, security
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   └── security.py
│   ├── models/         # SQLAlchemy models
│   │   ├── user.py
│   │   ├── workflow.py
│   │   ├── step.py
│   │   └── task.py
│   ├── schemas/        # Pydantic schemas
│   │   ├── user.py
│   │   ├── workflow.py
│   │   ├── step.py
│   │   └── task.py
│   ├── routers/        # API endpoints
│   │   ├── auth.py
│   │   ├── workflows.py
│   │   ├── steps.py
│   │   ├── tasks.py
│   │   ├── analytics.py
│   │   └── websocket.py
│   ├── utils/          # Utilities
│   │   └── email.py
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── tests/              # Test files
│   ├── test_state_machine.py
│   └── test_api.py
├── worker.py           # Background worker
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # PostgreSQL + Redis
├── alembic.ini         # Alembic configuration
├── .env.example        # Environment template
└── README_BACKEND.md   # This file
```

## Key Design Decisions

### 1. Why FastAPI?
- Modern, fast, with automatic API docs
- Native async support for WebSockets
- Type hints and Pydantic for validation
- Easy to test with TestClient

### 2. Why simple background worker instead of Celery?
- **Easier for beginners**: Just run `python worker.py`
- **No additional setup**: No need for message broker configuration
- **Sufficient for this use case**: Simple periodic checks
- **Easy to upgrade**: Can switch to Celery/RQ later if needed

For production with many background tasks, consider:
- **APScheduler**: More features, still simple
- **Celery**: Full-featured, requires RabbitMQ/Redis broker
- **RQ**: Simpler than Celery, Redis-based

### 3. State machine in the model
- Keeps business logic close to data
- Easy to test (no database needed)
- Can be validated before API calls
- Timestamps managed automatically

### 4. Redis pub/sub for WebSocket
- Decouples message publishing from WebSocket handling
- Multiple server instances can share messages
- Simple to implement and understand

## Troubleshooting

### Database connection fails
```bash
# Check PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Migrations fail
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d

# Run migrations again
alembic upgrade head
```

### Port already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it or use a different port
uvicorn app.main:app --reload --port 8001
```

### Tests fail with database errors
Tests use SQLite, not PostgreSQL. If you see errors:
```bash
# Remove test database
rm test.db

# Run tests again
pytest
```

## Next Steps

1. **Add more tests**: Coverage for analytics, WebSocket
2. **Add authentication to WebSocket**: Full JWT validation
3. **Implement real email**: Configure SMTP or SendGrid
4. **Add pagination**: For list endpoints with many results
5. **Add filtering/sorting**: Query parameters for list endpoints
6. **Add rate limiting**: Protect against abuse
7. **Deploy**: Use Docker, AWS, or other cloud platform
8. **Frontend**: Build React/Vue frontend to consume this API

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Redis Documentation](https://redis.io/docs/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## License

See LICENSE file.
