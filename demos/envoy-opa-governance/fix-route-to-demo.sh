#!/usr/bin/env bash
set -euo pipefail
NS=governance

echo "[1] Dump current envoy.yaml"
kubectl -n "$NS" get cm envoy-config -o jsonpath='{.data.envoy\.yaml}' > /tmp/envoy.yaml

echo "[2] Force route cluster -> demo_service"
# replace only route cluster lines, not ext_authz cluster
perl -0777 -i -pe '
  s/routes:\n(\s*-\s*match:\s*\{\s*prefix:\s*\"\/\"\s*\}\n\s*route:\s*\{\s*cluster:\s*)[^}]+(\s*\})/${1}demo_service${2}/g
' /tmp/envoy.yaml

echo "[3] Sanity check (show routes + clusters)"
grep -n "routes:" -n /tmp/envoy.yaml | head -n 5 || true
grep -n "cluster: demo_service" /tmp/envoy.yaml | head -n 20 || true
grep -n "cluster: authz_adapter" /tmp/envoy.yaml | head -n 20 || true

echo "[4] Apply ConfigMap"
kubectl -n "$NS" create cm envoy-config \
  --from-file=envoy.yaml=/tmp/envoy.yaml \
  -o yaml --dry-run=client | kubectl apply -f -

echo "[5] Restart Envoy"
kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy
