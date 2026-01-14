#!/usr/bin/env bash
set -euo pipefail

VAULT_ADDR="http://localhost:8200"
VAULT_TOKEN="galani-dev-token"

echo "Writing secrets to Vault (via HTTP API)..."

# ---- REPLACE VALUES BELOW ----
OPENAI_KEY="REPLACE_OPENAI_KEY"
ANTHROPIC_KEY="REPLACE_ANTHROPIC_KEY"
GITHUB_TOKEN="REPLACE_GITHUB_TOKEN"
# ------------------------------

# Write OpenAI
curl -sS -X POST "$VAULT_ADDR/v1/galani-secrets/data/openai" \
  -H "X-Vault-Token: $VAULT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"api_key\": \"$OPENAI_KEY\"}}" | python3 -m json.tool >/dev/null

# Write Anthropic
curl -sS -X POST "$VAULT_ADDR/v1/galani-secrets/data/anthropic" \
  -H "X-Vault-Token: $VAULT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"api_key\": \"$ANTHROPIC_KEY\"}}" | python3 -m json.tool >/dev/null

# Write GitHub
curl -sS -X POST "$VAULT_ADDR/v1/galani-secrets/data/github" \
  -H "X-Vault-Token: $VAULT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"data\": {\"token\": \"$GITHUB_TOKEN\"}}" | python3 -m json.tool >/dev/null

echo "✅ Secrets written. Reading back OpenAI secret (masked)..."
curl -sS "$VAULT_ADDR/v1/galani-secrets/data/openai" \
  -H "X-Vault-Token: $VAULT_TOKEN" | python3 -m json.tool | head -n 40
