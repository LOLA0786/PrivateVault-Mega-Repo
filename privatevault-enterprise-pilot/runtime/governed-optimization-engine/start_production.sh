#!/bin/bash
# Calculate number of workers based on CPU cores (MAANG Best Practice)
WORKERS=$(sysctl -n hw.ncpu)
echo "Starting OAAS with $WORKERS workers..."
uvicorn sovereign_api:app --host 0.0.0.0 --port 8000 --workers $WORKERS --log-level error
