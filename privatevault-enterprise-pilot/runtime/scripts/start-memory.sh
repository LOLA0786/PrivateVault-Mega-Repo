#!/usr/bin/env bash
echo "--- STARTING PRIVATEVAULT MEMORY & CONSOLE BRIDGE ---"

# Create the log file if it doesn't exist
touch /tmp/audit_chain.jsonl

# Start the Backend Bridge (Console) in the background
cd ~/PrivateVault-Console/backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &

echo ">>> SYSTEM ONLINE. GOVERNANCE RELAY ACTIVE."
