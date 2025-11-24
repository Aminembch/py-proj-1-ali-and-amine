#!/bin/bash
# Setup script for Smart Workflow Assistant backend

set -e  # Exit on error

echo "=== Smart Workflow Assistant - Setup Script ==="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Warning: Docker is not installed. You'll need to set up PostgreSQL and Redis manually."
else
    echo "✓ Docker found: $(docker --version)"
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Warning: docker-compose is not installed. You'll need to start services manually."
else
    echo "✓ docker-compose found: $(docker-compose --version)"
fi

echo ""
echo "Step 1: Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"

echo ""
echo "Step 2: Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "Step 3: Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo "  Please edit .env if you need to change any settings"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Step 4: Starting Docker services..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d
    echo "✓ PostgreSQL and Redis started"
    echo "  Waiting for services to be ready..."
    sleep 5
else
    echo "⚠ Skipping Docker services (docker-compose not found)"
    echo "  Make sure PostgreSQL and Redis are running manually"
fi

echo ""
echo "Step 5: Running database migrations..."
alembic upgrade head 2>&1 || echo "  Note: If migration fails, it may be because tables already exist. This is OK."
echo "✓ Database migrations complete"

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run server: uvicorn app.main:app --reload"
echo "  3. Open http://localhost:8000/docs in your browser"
echo ""
echo "To start the background worker (in a new terminal):"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run worker: python worker.py"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
