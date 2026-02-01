#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" get cm envoy-config -o jsonpath='{.data.envoy\.yaml}' > /tmp/envoy.yaml

# remove path_prefix line completely (most correct)
grep -v 'path_prefix:' /tmp/envoy.yaml > /tmp/envoy-fixed.yaml

kubectl -n "$NS" create cm envoy-config \
  --from-file=envoy.yaml=/tmp/envoy-fixed.yaml \
  -o yaml --dry-run=client | kubectl apply -f -

kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy
echo "✅ envoy fixed: ext_authz no longer prefixes /authz/<original_path>"
