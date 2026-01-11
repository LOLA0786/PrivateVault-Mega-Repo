#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" run heydeny --rm -i --restart=Never \
  --image=alpine:3.19 -- \
  sh -lc "
    set -e
    apk add --no-cache wget >/dev/null
    wget -qO /usr/local/bin/hey https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64
    chmod +x /usr/local/bin/hey

    echo 'DENY path (POST /delete) via Envoy+OPA'
    hey -n 2000 -c 50 -m POST http://envoy:8080/delete | tee /tmp/deny.txt

    echo '---- p95/p99 ----'
    grep -E '  95%|  99%' /tmp/deny.txt || true
  "
