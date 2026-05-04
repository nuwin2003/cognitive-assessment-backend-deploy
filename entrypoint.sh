#!/bin/bash

# Start the main FastAPI application in the background
echo "Starting main backend API on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
MAIN_PID=$!

# Start the movement prediction API in the background
echo "Starting movement prediction API on port 8001..."
uvicorn movement_predict_api:app --host 0.0.0.0 --port 8001 &
MOVEMENT_PID=$!

# Wait for both processes
wait $MAIN_PID $MOVEMENT_PID

# If any process exits, exit the container
exit $?
