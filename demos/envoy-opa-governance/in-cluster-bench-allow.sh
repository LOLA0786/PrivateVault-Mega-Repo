#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" run hey2 --rm -i --restart=Never \
  --image=alpine:3.19 -- \
  sh -lc "
    set -e
    apk add --no-cache wget >/dev/null
    wget -qO /usr/local/bin/hey https://hey-release.s3.us-east-2.amazonaws.com/hey_linux_amd64
    chmod +x /usr/local/bin/hey

    echo 'BASELINE allow (direct demo GET /)'
    hey -n 5000 -c 50 http://demo:9000/ | tee /tmp/base.txt

    echo 'ENVOY+OPA allow (GET /)'
    hey -n 5000 -c 50 http://envoy:8080/ | tee /tmp/enforced.txt

    echo '---- p95/p99 ----'
    echo 'Baseline:'
    grep -E '  95%|  99%' /tmp/base.txt || true
    echo 'Envoy+OPA:'
    grep -E '  95%|  99%' /tmp/enforced.txt || true
  "
