#!/usr/bin/env bash
set -euo pipefail
NS="governance"

kubectl -n "$NS" run opatest --rm -i --restart=Never \
  --image=curlimages/curl:8.5.0 -- \
  sh -lc '
    echo "POST /delete must be denied:"
    curl -s http://opa:8181/v1/data/envoy/authz \
      -H "content-type: application/json" \
      -d "{\"input\":{\"attributes\":{\"request\":{\"http\":{\"method\":\"POST\",\"path\":\"/delete\"}}}}}" | head -c 300
    echo
    echo "POST /deploy must require approval:"
    curl -s http://opa:8181/v1/data/envoy/authz \
      -H "content-type: application/json" \
      -d "{\"input\":{\"attributes\":{\"request\":{\"http\":{\"method\":\"POST\",\"path\":\"/deploy\"}}}}}" | head -c 300
    echo
  '
