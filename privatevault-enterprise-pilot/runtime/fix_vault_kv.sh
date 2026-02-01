#!/usr/bin/env bash
set -euo pipefail

echo "[1/3] Checking Vault status..."
docker exec -i galani-vault sh -lc '
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=galani-dev-token
vault status
'

echo "[2/3] Enabling KV-v2 at path galani-secrets (idempotent)..."
docker exec -i galani-vault sh -lc '
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=galani-dev-token

vault secrets enable -path=galani-secrets kv-v2 || true
vault secrets list
'

echo "[3/3] Re-running migration + smoke test..."
python3 scripts/migrate_api_keys.py
python3 examples/use_secrets_manager.py

echo "✅ Vault KV + migration fixed"
