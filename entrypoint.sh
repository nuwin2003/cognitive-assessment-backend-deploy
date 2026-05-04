#!/bin/bash
set -e

# Function to handle errors
handle_error() {
    echo "Error: A service failed to start"
    kill $(jobs -p) 2>/dev/null || true
    exit 1
}

trap handle_error ERR

# Start the main FastAPI application in the background
echo "Starting main backend API on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 > /var/log/main_api.log 2>&1 &
MAIN_PID=$!
echo "Main API PID: $MAIN_PID"

# Give the main API time to start
sleep 2

# Start the movement prediction API in the background
echo "Starting movement prediction API on port 8001..."
uvicorn movement_predict_api:app --host 0.0.0.0 --port 8001 > /var/log/movement_api.log 2>&1 &
MOVEMENT_PID=$!
echo "Movement API PID: $MOVEMENT_PID"

echo "Both services started. Main API: PID $MAIN_PID, Movement API: PID $MOVEMENT_PID"
echo "Logs: /var/log/main_api.log and /var/log/movement_api.log"

# Wait for all background processes
wait
