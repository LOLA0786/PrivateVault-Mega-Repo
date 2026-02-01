#!/usr/bin/env bash
echo "--- Testing PrivateVault v2 Temporal Enforcement ---"

# Step 1: Fire 5 successful-looking requests
for i in {1..5}; do
  RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -XPOST http://envoy:8080/delete)
  echo "Attempt $i: HTTP $RESPONSE (Expected 403 but with 'allow:true' logic if under limit)"
done

# Step 2: The 6th request should trigger the Relay's 'temporal_limit_exceeded'
echo "Attempt 6: Triggering threshold..."
FINAL_RESP=$(curl -s -XPOST http://envoy:8080/delete)
echo "Server Response: $FINAL_RESP"

if [[ "$FINAL_RESP" == *"temporal_limit_exceeded"* ]]; then
  echo "✅ TEST PASSED: Temporal context correctly blocked the agent."
else
  echo "❌ TEST FAILED: System did not enforce the sliding window."
fi
