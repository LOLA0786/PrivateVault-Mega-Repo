#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" run curl --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  sh -lc '
    set +e

    echo "=== GET / via envoy ==="
    curl -m 3 -sS -i http://envoy:8080/ | sed -n "1,25p"
    echo

    echo "=== POST /delete via envoy ==="
    curl -m 3 -sS -i -XPOST http://envoy:8080/delete | sed -n "1,50p"
    echo

    echo "=== POST /deploy via envoy ==="
    curl -m 3 -sS -i -XPOST http://envoy:8080/deploy | sed -n "1,60p"
    echo
  '
