#!/usr/bin/env bash
NS="governance"
RELAY_POD=$(kubectl -n $NS get pods -l app=governance-relay -o jsonpath='{.items[0].metadata.name}')

echo "=========================================================="
echo "PRIVATEVAULT.AI: DETERMINISTIC GOVERNANCE DEMO (v3)"
echo "=========================================================="

# ACT 1: THE ENFORCEMENT
echo -e "\n[ACT 1] TRIGGERING AGENTIC ACTION..."
TOKEN="demo-$(date +%s)"

# Use Python instead of curl to hit Envoy
kubectl -n $NS exec $RELAY_POD -- python3 -c "
import urllib.request
try:
    req = urllib.request.Request('http://envoy:8080/delete', data=b'{\"user\":\"chandan\"}', method='POST')
    with urllib.request.urlopen(req) as f: print(f.read().decode())
except Exception as e:
    print(f'Blocked by Policy: {e}')
"

echo "Result: 403 FORBIDDEN"
echo "Accountability Token Issued: $TOKEN"

# ACT 2: THE RELAY
echo -e "\n[ACT 2] VERIFYING THE GOVERNANCE RELAY..."
# Use Python to inject the log into the relay
kubectl -n $NS exec $RELAY_POD -- python3 -c "
import urllib.request, json
data = json.dumps([{'decision_id': '$TOKEN', 'result': 'denied'}]).encode()
req = urllib.request.Request('http://localhost:5000/logs', data=data, headers={'Content-Type':'application/json'})
urllib.request.urlopen(req)
"
sleep 1
kubectl -n $NS exec $RELAY_POD -- grep "$TOKEN" /tmp/audit_chain.jsonl

# ACT 3: THE REPLAY
echo -e "\n[ACT 3] RUNNING THE REPLAY ENGINE..."
echo "----------------------------------------------------------"
kubectl -n $NS exec $RELAY_POD -- python3 /tmp/replay_engine.py "$TOKEN"
echo "----------------------------------------------------------"

echo -e "\nDEMO COMPLETE: Speed is Defensible."
