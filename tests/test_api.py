"""
API endpoint tests using FastAPI TestClient.
Tests authentication and basic CRUD operations.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Mock Redis for tests (no Redis server needed)
mock_redis = Mock()
mock_redis.publish = Mock(return_value=None)
mock_redis.sismember = Mock(return_value=False)
mock_redis.sadd = Mock(return_value=None)

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Patch Redis client to use mock
    with patch('app.core.redis_client.redis_client', mock_redis):
        yield TestClient(app)
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["status"] == "running"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "role": "user"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned


def test_register_duplicate_email(client):
    """Test that duplicate email registration fails."""
    # Register first user
    client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "different123"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login_success(client):
    """Test successful login."""
    # Register user
    client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    # Login
    response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test login with wrong password."""
    # Register user
    client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    # Try login with wrong password
    response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


def test_create_workflow_requires_auth(client):
    """Test that creating a workflow requires authentication."""
    response = client.post(
        "/workflows/",
        json={"name": "Test Workflow"}
    )
    assert response.status_code == 401  # Unauthorized


def test_create_workflow_authenticated(client):
    """Test creating a workflow when authenticated."""
    # Register and login
    client.post(
        "/register",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    login_response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create workflow
    response = client.post(
        "/workflows/",
        json={"name": "My Workflow"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Workflow"
    assert "id" in data
    assert "owner_id" in data


def test_task_state_transition_via_api(client):
    """Test task state transitions through the API."""
    # Setup: Register, login, create workflow, step, and task
    client.post(
        "/register",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    login_response = client.post(
        "/login",
        json={"email": "test@example.com", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create workflow
    workflow_response = client.post(
        "/workflows/",
        json={"name": "Test Workflow"},
        headers=headers
    )
    workflow_id = workflow_response.json()["id"]
    
    # Create step
    step_response = client.post(
        f"/workflows/{workflow_id}/steps/",
        json={"name": "Step 1", "order": 1, "expected_duration_hours": 2.0},
        headers=headers
    )
    step_id = step_response.json()["id"]
    
    # Create task
    task_response = client.post(
        "/tasks/",
        json={"step_id": step_id, "title": "Test Task", "description": "Test"},
        headers=headers
    )
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]
    assert task_response.json()["status"] == "pending"
    
    # Transition to in_progress
    transition_response = client.post(
        f"/tasks/{task_id}/transition",
        json={"desired_state": "in_progress"},
        headers=headers
    )
    assert transition_response.status_code == 200
    assert transition_response.json()["status"] == "in_progress"
    
    # Try invalid transition (in_progress -> pending should fail)
    invalid_transition = client.post(
        f"/tasks/{task_id}/transition",
        json={"desired_state": "pending"},
        headers=headers
    )
    assert invalid_transition.status_code == 400
    assert "Invalid transition" in invalid_transition.json()["detail"]
    
    # Valid transition to done
    done_transition = client.post(
        f"/tasks/{task_id}/transition",
        json={"desired_state": "done"},
        headers=headers
    )
    assert done_transition.status_code == 200
    assert done_transition.json()["status"] == "done"
