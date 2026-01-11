#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" run curl2 --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  sh -lc '
    echo "=== DEBUG HEADERS delete ==="
    curl -is -XPOST http://envoy:8080/delete | grep -i "x-dbg" || true
    echo "=== DEBUG HEADERS deploy ==="
    curl -is -XPOST http://envoy:8080/deploy | grep -i "x-dbg" || true
  '
