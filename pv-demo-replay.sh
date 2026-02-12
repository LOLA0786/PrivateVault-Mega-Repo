#!/usr/bin/env bash

echo "=== PRIVATEVAULT REPLAY DEMO ==="

REQ='{"prompt":"Approve loan 250000 for ACME"}'

echo "Original:"
curl -s -X POST http://127.0.0.1:8000/execute \
 -H "Content-Type: application/json" \
 -d "$REQ"

echo ""
echo "Replay:"

curl -s -X POST http://127.0.0.1:8000/execute \
 -H "Content-Type: application/json" \
 -d "$REQ"

python3 replay_protection.py | tail -10
