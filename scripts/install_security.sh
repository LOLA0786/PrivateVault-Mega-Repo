#!/bin/bash
# Install security dependencies

set -e

echo "Installing security dependencies..."
pip install -r requirements-security.txt

echo "Creating directories..."
mkdir -p security/auth
mkdir -p security/secrets
mkdir -p security/validation
mkdir -p vault/config
mkdir -p vault/data

echo "Starting Vault..."
docker-compose -f docker-compose.vault.yml up -d

echo "Waiting for Vault to start..."
sleep 5

# Initialize Vault
docker exec -it galani-vault vault secrets enable -path=galani-secrets kv-v2

echo ""
echo "✅ Security setup complete!"
echo ""
echo "Next steps:"
echo "1. Run: python3 scripts/migrate_api_keys.py"
echo "2. Verify: docker exec -it galani-vault vault kv list galani-secrets/"
echo "3. Delete api_keys.json: rm api_keys.json"
echo "4. Commit: git add -A && git commit -m 'SECURITY: Added Vault + Auth'"
