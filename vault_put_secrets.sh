#!/usr/bin/env bash
set -euo pipefail

export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="galani-dev-token"

echo "Writing secrets to Vault..."

# IMPORTANT: replace values below
vault kv put galani-secrets/openai api_key="REPLACE_OPENAI_KEY"
vault kv put galani-secrets/anthropic api_key="REPLACE_ANTHROPIC_KEY"
vault kv put galani-secrets/github token="REPLACE_GITHUB_TOKEN"

echo "Reading back (proof)..."
vault kv get galani-secrets/openai
