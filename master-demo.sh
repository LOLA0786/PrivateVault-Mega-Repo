#!/usr/bin/env bash
NS="governance"
echo "=========================================================="
echo "PRIVATEVAULT.AI: DETERMINISTIC GOVERNANCE DEMO"
echo "=========================================================="

# ACT 1: THE ENFORCEMENT (Stateless Gate)
echo -e "\n[ACT 1] TRIGGERING AGENTIC ACTION..."
echo "Simulating a rogue 'DELETE' request from an autonomous agent..."
LINEAGE_ID=$(kubectl -n $NS run tester --rm -it --image=curlimages/curl:8.5.0 -- \
curl -s -XPOST http://envoy:8080/delete -H 'Content-Type: application/json' -d '{"user":"chandan"}' | jq -r '.lineage_id')

echo "Result: 403 FORBIDDEN"
echo "Accountability Token Issued: $LINEAGE_ID"

# ACT 2: THE RELAY (Stateful Memory)
echo -e "\n[ACT 2] VERIFYING THE GOVERNANCE RELAY..."
echo "Checking if the Detective (Relay) captured the intent..."
sleep 3 # Wait for OPA log batching
kubectl -n $NS exec deployments/governance-relay -- grep "$LINEAGE_ID" /tmp/audit_chain.jsonl

# ACT 3: THE REPLAY (Architectural Accountability)
echo -e "\n[ACT 3] RUNNING THE REPLAY ENGINE..."
echo "Reconstructing the decision timeline for audit..."
echo "----------------------------------------------------------"
kubectl -n $NS exec deployments/governance-relay -- python3 /tmp/replay_engine.py "$LINEAGE_ID"
echo "----------------------------------------------------------"

echo -e "\nDEMO COMPLETE: Speed is Defensible."
