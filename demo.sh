#!/bin/bash

set -e

echo "===================================="
echo "  PrivateVault Enterprise Demo"
echo "===================================="

echo "[1/4] Starting services..."
docker-compose up -d

sleep 5

echo "[2/4] Running governance demo..."
python demo_all_in_one.py

echo "[3/4] Running security demo..."
python galani_fintech_demo.py

echo "[4/4] Showing audit proof..."
python inspect_audit_log.py

echo "===================================="
echo "Demo Ready"
echo "Open: http://localhost:8000"
echo "===================================="
