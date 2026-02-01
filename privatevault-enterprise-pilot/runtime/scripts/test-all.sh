#!/usr/bin/env bash
set -euo pipefail

NS="governance"

echo "=== [1/9] VERIFY REPO CONSISTENCY ==="
make verify

echo "=== [2/9] CHECK K8S HEALTH ==="
kubectl -n "$NS" get pods | egrep 'envoy|authz-adapter|governance-relay|pv-authority-resolver|redis-state'

echo "=== [3/9] PORT-FORWARD ENVOY (8080) + ADMIN (9901) ==="
kubectl -n "$NS" port-forward svc/envoy 8080:8080 9901:9901 >/tmp/pf_envoy.log 2>&1 &
PF_ENVOY=$!
cleanup() { kill $PF_ENVOY >/dev/null 2>&1 || true; }
trap cleanup EXIT
sleep 2

echo "=== [4/9] ENVOY EXT_AUTHZ STATS (BEFORE) ==="
curl -s http://localhost:9901/stats | grep -i ext_authz | head -n 30 || true

echo "=== [5/9] TEST: ALLOW PATH (GET /) ==="
curl -sS -i http://localhost:8080/ | head -n 20 | tee /tmp/pv_allow_headers.txt
grep -q "200 OK" /tmp/pv_allow_headers.txt

echo "=== [6/9] TEST: DENY ACTION (POST /delete) ==="
curl -sS -i -X POST http://localhost:8080/delete \
  -H "Content-Type: application/json" \
  -d '{"op":"delete"}' | tee /tmp/pv_deny_response.txt | head -n 40

grep -q "403 Forbidden" /tmp/pv_deny_response.txt
grep -q "delete_denied_by_policy" /tmp/pv_deny_response.txt

echo "=== [7/9] ENVOY EXT_AUTHZ STATS (AFTER) ==="
curl -s http://localhost:9901/stats | grep -i ext_authz | head -n 30 || true

echo "=== [8/9] CHECK AUTHORITYBINDINGS PRESENT ==="
kubectl -n "$NS" get authoritybindings

echo "=== [9/9] DONE ==="
echo "✅ FULL E2E TEST PASSED (Envoy -> ext_authz -> OPA policy -> deny/allow verified)"
