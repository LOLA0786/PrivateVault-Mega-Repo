#!/usr/bin/env bash
set -e

echo "===================================="
echo "PrivateVault Enterprise Installer"
echo "===================================="

echo "Checking kubectl availability..."
if ! command -v kubectl >/dev/null 2>&1; then
  echo "ERROR: kubectl is not installed"
  exit 1
fi

echo "Checking Kubernetes cluster connectivity..."
if ! kubectl cluster-info >/dev/null 2>&1; then
  echo "ERROR: No active Kubernetes cluster detected."
  echo "Please configure kubectl context before installing."
  echo "Examples: GKE / EKS / AKS / kind / minikube"
  exit 1
fi

NAMESPACE="pv-pilot"

echo "Ensuring namespace exists: $NAMESPACE"
kubectl create namespace $NAMESPACE \
  --dry-run=client -o yaml | kubectl apply -f -

echo "Cluster check passed."
echo "Starting deployment..."
echo "===================================="

# ---- Original script continues below ----
echo "Deploying PrivateVault Enterprise Pilot..."

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml

echo "Waiting for pods..."
kubectl wait --for=condition=ready pod \
  -l app=privatevault \
  -n pv-pilot \
  --timeout=180s

echo "Deployment successful."
kubectl get pods -n pv-pilot
