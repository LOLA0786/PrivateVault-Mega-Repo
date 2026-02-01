#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" run curl3 --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  sh -lc '
    echo "=== ext_authz stats ==="
    curl -s http://envoy:9901/stats | grep -i ext_authz || true
  '
