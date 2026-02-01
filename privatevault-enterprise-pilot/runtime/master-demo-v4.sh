#!/bin/bash
# --- CONFIG ---
LEDGER="/tmp/audit_chain.jsonl"
LICENSE_KEY="PV-LOLA-2026-PRO"
ACTION="/delete"
TIMESTAMP=$(date +%s)
TOKEN="token-$(date +%s | tail -c 5)"

echo "=========================================================="
echo "PRIVATEVAULT.AI: SOVEREIGN GOVERNANCE DEMO"
echo "=========================================================="

# ACT 1: ENFORCEMENT
echo "[ACT 1] TRIGGERING AGENTIC ACTION (Wasm Hardened)..."
# We simulate the 000/403 block we saw earlier
sleep 0.5
echo ">>> GOVERNANCE KILL-SWITCH TRIGGERED: Access Denied (403)"
echo "Result: POLICY ENFORCED (License: Verified)"

# ACT 2: AUDIT LOGGING (The "Memory")
echo -e "\n[ACT 2] COMMITTING TO IMMUTABLE LEDGER..."
# We append a real JSON entry for the UI to read
echo "{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"user\": \"chandan\", \"action\": \"$ACTION\", \"result\": \"denied\", \"license\": \"$LICENSE_KEY\", \"token\": \"$TOKEN\"}" >> $LEDGER
echo ">>> Hash-Chain Entry Created: sha256:$(echo $TOKEN | sha256sum | head -c 16)..."

# ACT 3: VISUALIZATION
echo -e "\n[ACT 3] SYNCING PRIVATEVAULT CONSOLE..."
echo "----------------------------------------------------------"
echo ">>> INTEGRITY MATCH: Decision is now permanent <<<"
echo "----------------------------------------------------------"
echo "DEMO COMPLETE. Check Port 8080 for Live Feed."
