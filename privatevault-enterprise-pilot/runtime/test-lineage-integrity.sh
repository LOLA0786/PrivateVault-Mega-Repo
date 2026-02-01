#!/usr/bin/env bash
echo "--- Verifying Decision Lineage ---"

# 1. Generate a rejected request and capture the Lineage ID
LINEAGE_ID=$(curl -s -XPOST http://envoy:8080/delete | jq -r '.lineage_id')
echo "Captured Lineage ID from Response: $LINEAGE_ID"

# 2. Search for this ID in the Relay's Audit Chain
echo "Searching Audit Chain for evidence..."
AUDIT_MATCH=$(kubectl -n governance exec deployments/governance-relay -- grep "$LINEAGE_ID" /tmp/audit_chain.jsonl)

if [ ! -z "$AUDIT_MATCH" ]; then
  echo "✅ LINEAGE VERIFIED: Evidence found in immutable store."
  echo "Evidence Record: $AUDIT_MATCH"
else
  echo "❌ LINEAGE FAILED: Decision was made but no evidence was recorded."
fi
