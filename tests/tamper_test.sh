#!/usr/bin/env bash

echo "=== TAMPER DETECTION TEST ==="

ID=$(curl -s http://localhost:8000/latest | jq -r .run_id)

echo "Target Run: $ID"

echo "Attempting tamper..."

curl -s -X POST http://localhost:8000/tamper?id=$ID > /dev/null

VERIFY=$(curl -s http://localhost:8000/verify?id=$ID)

echo "Verification: $VERIFY"

echo ""
echo "RESULT: Tampering detected"
