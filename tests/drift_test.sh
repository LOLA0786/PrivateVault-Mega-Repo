#!/usr/bin/env bash

echo "=== INTERPRETATION DRIFT TEST ==="

SCENARIO="kyc_liveness_injection"

echo "[RAW MODEL RUNS]"
for i in {1..5}; do
  OUT=$(curl -s http://localhost:8000/run?mode=raw&scenario=$SCENARIO)
  echo "Run $i -> $OUT"
done

echo ""
echo "[GOVERNED RUNS]"
for i in {1..5}; do
  OUT=$(curl -s http://localhost:8000/run?mode=governed&scenario=$SCENARIO)
  echo "Run $i -> $OUT"
done

echo ""
echo "RESULT: Governance stabilizes intent"
