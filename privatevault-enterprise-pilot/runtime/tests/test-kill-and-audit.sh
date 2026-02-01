#!/usr/bin/env bash
echo "--- ACT 1: TRIGGERING VIOLATION ---"
# Trigger a blocked action and capture the token
TOKEN="test-$(date +%s)"
RELAY_POD=$(kubectl -n governance get pods -l app=governance-relay -o jsonpath='{.items[0].metadata.name}')

# Simulate blocked request
kubectl -n governance exec $RELAY_POD -- python3 -c "
import urllib.request, json
# Manually simulate the OPA decision being sent to the relay with our chain generator
from chain_generator import LineageLedger
ledger = LineageLedger()
ledger.sign_decision({'decision_id': '$TOKEN', 'user': 'chandan', 'action': '/delete'})
"

echo "--- ACT 2: VERIFYING CRYPTOGRAPHIC INTEGRITY ---"
# Run our verify-integrity.py against the ledger
kubectl -n governance exec $RELAY_POD -- python3 /tmp/verify-integrity.py /tmp/audit_chain.jsonl

if [ $? -eq 0 ]; then
  echo "✅ TEST PASSED: Audit trail is untampered and linked."
else
  echo "❌ TEST FAILED: Hash-chain corruption detected!"
fi
