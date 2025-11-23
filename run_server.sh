#!/bin/bash
# Quick start script for running the server

echo "Starting Smart Workflow Assistant API Server..."
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
