#!/usr/bin/env bash
NS="governance"

# 1. Simulate a sequence of events
echo "Simulating 6 'DELETE' attempts to trigger temporal logic..."
for i in {1..6}; do
  curl -s -XPOST http://envoy:8080/delete > /dev/null
done

# 2. Extract the last Lineage ID from the Relay
echo "Fetching last Lineage ID from Audit Chain..."
LAST_ID=$(kubectl -n $NS exec -it deployments/governance-relay -- tail -n 1 /tmp/audit_chain.jsonl | jq -r '.lineage_id')

echo "Identified Lineage ID: $LAST_ID"
echo "----------------------------------------"

# 3. Run Replay
kubectl -n $NS exec -it deployments/governance-relay -- python3 /mnt/replay_engine.py $LAST_ID
