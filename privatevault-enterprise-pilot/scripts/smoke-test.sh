#!/usr/bin/env bash
set -e

NAMESPACE="pv-pilot"
APP_LABEL="app=privatevault"

echo "===================================="
echo "PrivateVault Enterprise Smoke Test"
echo "===================================="

echo "[1/4] Checking Kubernetes access..."
kubectl version --client >/dev/null

echo "[2/4] Checking namespace: $NAMESPACE"
kubectl get ns $NAMESPACE >/dev/null 2>&1 || {
  echo "ERROR: Namespace $NAMESPACE not found"
  exit 1
}

echo "[3/4] Waiting for PrivateVault pods..."
kubectl wait \
  --for=condition=ready pod \
  -l $APP_LABEL \
  -n $NAMESPACE \
  --timeout=120s

echo "[4/4] Verifying receipt generation..."

LOGS=$(kubectl logs -n $NAMESPACE -l $APP_LABEL --tail=200)

echo "$LOGS" | grep -q "Receipt" && {
  echo "PASS: Receipt evidence detected"
} || {
  echo "FAIL: No receipt evidence found"
  exit 1
}

echo "===================================="
echo "Smoke test PASSED"
echo "PrivateVault is operational"
echo "===================================="
