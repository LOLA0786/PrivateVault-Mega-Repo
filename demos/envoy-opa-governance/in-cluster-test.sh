#!/usr/bin/env bash
set -euo pipefail

NS="governance"

kubectl -n "$NS" run curl --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  sh -lc '
    set -e
    echo "=== GET / via envoy ==="
    curl -i http://envoy:8080/ | head -n 20
    echo
    echo "=== POST /delete via envoy ==="
    curl -i -XPOST http://envoy:8080/delete | head -n 30
    echo
    echo "=== POST /deploy via envoy ==="
    curl -i -XPOST http://envoy:8080/deploy | head -n 30
  '
