#!/usr/bin/env bash
set -euo pipefail
NS="governance"

# overwrite envoy config with correct adapter port (8000)
kubectl -n "$NS" get cm envoy-config -o jsonpath='{.data.envoy\.yaml}' \
  | sed 's/authz-adapter, port_value: 8081/authz-adapter, port_value: 8000/g' \
  | sed 's|uri: http://authz-adapter:8081|uri: http://authz-adapter:8000|g' \
  > /tmp/envoy.yaml

kubectl -n "$NS" create cm envoy-config --from-file=envoy.yaml=/tmp/envoy.yaml -o yaml --dry-run=client | kubectl apply -f -

kubectl -n "$NS" rollout restart deploy/envoy
kubectl -n "$NS" rollout status deploy/envoy
