#!/usr/bin/env bash
set -euo pipefail

NS="governance"
NO_PF="${NO_PF:-0}"

echo "=== [1/9] VERIFY ==="
make verify

echo "=== [2/9] GUARDS ==="
./scripts/security-guard.sh

echo "=== [3/9] CLUSTER HEALTH ==="
kubectl -n "$NS" get pods | egrep 'envoy|authz-adapter|governance-relay|pv-authority-resolver|redis-state'

if [[ "$NO_PF" == "0" ]]; then
  echo "=== [4/9] PORT-FORWARD ENVOY ==="
  kubectl -n "$NS" port-forward svc/envoy 8080:8080 9901:9901
  exit 0
fi

echo "=== [4/9] EXT_AUTHZ STATS BEFORE ==="
BEFORE_OK=$(curl -s http://localhost:9901/stats | awk '/http.ingress_http.ext_authz.ok:/ {print $2}')
BEFORE_DENY=$(curl -s http://localhost:9901/stats | awk '/http.ingress_http.ext_authz.denied:/ {print $2}')
echo "before ok=$BEFORE_OK deny=$BEFORE_DENY"

echo "=== [5/9] GOLD: ALLOW (GET /) ==="
curl -sS -i http://localhost:8080/ | head -n 20 | tee /tmp/pv_gold_allow.txt
grep -q "200 OK" /tmp/pv_gold_allow.txt

echo "=== [6/9] GOLD: DENY (POST /delete) ==="
curl -sS -i -X POST http://localhost:8080/delete \
  -H "Content-Type: application/json" \
  -d '{"op":"delete"}' | tee /tmp/pv_gold_deny.txt | head -n 40
grep -q "403 Forbidden" /tmp/pv_gold_deny.txt
grep -q "delete_denied_by_policy" /tmp/pv_gold_deny.txt

echo "=== [7/9] EXT_AUTHZ STATS AFTER ==="
AFTER_OK=$(curl -s http://localhost:9901/stats | awk '/http.ingress_http.ext_authz.ok:/ {print $2}')
AFTER_DENY=$(curl -s http://localhost:9901/stats | awk '/http.ingress_http.ext_authz.denied:/ {print $2}')
echo "after ok=$AFTER_OK deny=$AFTER_DENY"

echo "=== [8/9] AUTHORITY REGISTRY EXISTS ==="
kubectl -n "$NS" get authoritybindings

echo "=== [9/9] DONE ==="
echo "✅ GOLD TEST PASS"
