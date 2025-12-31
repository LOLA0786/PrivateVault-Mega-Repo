# PrivateVault Mega Repo

Unified control + execution platform for AI systems.

## Components

### 1. Intent Engine (Control Plane)
- Deterministic pre-execution authorization
- Policy-based decisions
- Cryptographic evidence & audit

Runs on: `localhost:8000`

### 2. PrivateVault (Execution Plane)
- Secure execution layer
- Isolated actions
- Vault-backed operations

Runs on: `localhost:8001`

### 3. Gateway (Unified Entry)
- Single API for clients
- Calls Intent Engine before execution
- Enforces allow / block with evidence

Runs on: `localhost:8002`

## Local Run (3 terminals)

### Terminal 1 – Intent Engine
```bash
cd intent_engine
uvicorn main:app --reload --port 8000

Terminal 2 – PrivateVault
cd privatevault
uvicorn vault_api:app --reload --port 8001

Terminal 3 – Gateway
cd gateway
uvicorn app:app --reload --port 8002

End-to-End Test
curl -X POST http://localhost:8002/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "transfer_money",
    "args": {"amount": 250000},
    "context": {"jurisdiction": "IN"}
  }'


Expected:

BLOCKED for high-risk actions

EXECUTED for allowed actions

This repo represents the full working system.
