#!/bin/bash

if [ "$RUN_MODE" = "worker" ]; then
    echo "Starting workers..."
    python worker.py
else
    echo "Starting API..."
    uvicorn main:app --host 0.0.0.0 --port 8000
fi