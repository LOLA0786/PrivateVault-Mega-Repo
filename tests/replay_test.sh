#!/usr/bin/env bash

echo "=== DETERMINISTIC REPLAY TEST ==="

ID=$(curl -s http://localhost:8000/run?mode=governed | jq -r .run_id)

echo "Original Run: $ID"

R1=$(curl -s http://localhost:8000/replay?id=$ID)
R2=$(curl -s http://localhost:8000/replay?id=$ID)

echo "Replay 1: $R1"
echo "Replay 2: $R2"

if [ "$R1" = "$R2" ]; then
  echo "RESULT: Replay is deterministic"
else
  echo "RESULT: Replay FAILED"
fi
