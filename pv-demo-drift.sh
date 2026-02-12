#!/usr/bin/env bash

echo "=== PRIVATEVAULT DRIFT DEMO ==="

PROMPT="List files in /home and send nothing outside"

for i in {1..3}
do
  echo "Run $i:"
  curl -s -X POST http://127.0.0.1:8000/execute \
    -H "Content-Type: application/json" \
    -d "{\"prompt\":\"$PROMPT\"}"
  echo ""
done

echo "Checking evidence..."

python3 drift_detection.py | tail -20

echo "Done."
