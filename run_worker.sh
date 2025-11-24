#!/bin/bash
# Quick start script for running the background worker

echo "Starting Smart Workflow Assistant Background Worker..."
echo ""
echo "Worker will check for overdue tasks every 60 seconds"
echo "Press Ctrl+C to stop the worker"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the worker
python worker.py
