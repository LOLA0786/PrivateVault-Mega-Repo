#!/usr/bin/env bash
set -e

NAMESPACE="pv-pilot"
APP_LABEL="app=privatevault"

echo "=========================================="
echo " PrivateVault Enterprise Governance Demo "
echo "=========================================="
echo
echo "This demo shows how PrivateVault:"
echo " - Enforces AI governance policies"
echo " - Generates cryptographic evidence"
echo " - Detects tampering"
echo " - Enables forensic verification"
echo

sleep 2

echo "[1/5] Installing PrivateVault..."
./scripts/install.sh

echo
echo "[2/5] Waiting for system stabilization..."
sleep 15

echo
echo "[3/5] Locating PrivateVault pod..."

POD=$(kubectl get pods -n $NAMESPACE -l $APP_LABEL \
  -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD" ]; then
  echo "ERROR: No PrivateVault pod found"
  exit 1
fi

echo "Found pod: $POD"

echo
echo "[4/5] Extracting cryptographic receipt..."

kubectl exec -n $NAMESPACE $POD -- \
  cat /app/receipt.json > demo-receipt.json

echo "Receipt saved to: demo-receipt.json"

echo
echo "[5/5] Verifying evidence integrity..."

./scripts/verify-evidence.sh demo-receipt.json

echo
echo "Verification successful."
echo "This proves the AI action is:"
echo " - Authenticated"
echo " - Untampered"
echo " - Reproducible"

sleep 2

echo
echo "------------------------------------------"
echo "Simulating unauthorized tampering..."
echo "------------------------------------------"

sed -i 's/outputs-demo-hash/hacked/' demo-receipt.json 2>/dev/null || true

echo "Tampering injected."

echo
echo "Re-verifying evidence (expected to fail)..."

if ./scripts/verify-evidence.sh demo-receipt.json; then
  echo "ERROR: Tampering was NOT detected"
  exit 1
else
  echo "PASS: Tampering detected and blocked"
fi

echo
echo "=========================================="
echo " Demo Completed Successfully"
echo "=========================================="
echo
echo "Result:"
echo "PrivateVault provides defensible, auditable,"
echo "and regulator-ready AI governance."
echo
