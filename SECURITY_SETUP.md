# Security Setup Guide

## Quick Start (Copy-Paste These Commands)

```bash
# 1. Install dependencies
pip install -r requirements-security.txt

# 2. Start Vault
docker-compose -f docker-compose.vault.yml up -d

# 3. Wait for Vault to be ready
sleep 5

# 4. Enable secrets engine
docker exec galani-vault vault secrets enable -path=galani-secrets kv-v2

# 5. Migrate API keys (if you have api_keys.json)
python3 scripts/migrate_api_keys.py

# 6. Verify migration
docker exec galani-vault vault kv list galani-secrets/

# 7. Test getting a secret
python3 -c "
from security.secrets.secrets_manager import get_secrets_manager
secrets = get_secrets_manager()
print(secrets.get_secret('openai/api_key'))
"

# 8. DELETE the old api_keys.json file
rm api_keys.json

# 9. Commit changes
git add -A
git commit -m "SECURITY: Migrated to Vault + Added Auth + Input Validation"
git push origin main
```

## What Was Created

1. **HashiCorp Vault** - Secure secrets storage
   - Location: `docker-compose.vault.yml`
   - Access: http://localhost:8200
   - Token: `galani-dev-token` (DEV ONLY)

2. **Secrets Manager** - Python wrapper for Vault
   - Location: `security/secrets/secrets_manager.py`
   - Usage: See `examples/use_secrets_manager.py`

3. **JWT Authentication** - Secure API endpoints
   - Location: `security/auth/jwt_auth.py`
   - Usage: See `examples/add_auth_to_endpoint.py`

4. **Input Validation** - Prevent injection attacks
   - Location: `security/validation/validators.py`
   - Usage: See `examples/use_input_validation.py`

## Testing

```bash
# Test Vault connection
docker exec galani-vault vault status

# Test secrets manager
python3 examples/use_secrets_manager.py

# Test authentication (start FastAPI app first)
python3 examples/add_auth_to_endpoint.py
```

## Production Checklist

- [ ] Change Vault root token (not using dev mode)
- [ ] Use Vault auto-unseal with cloud KMS
- [ ] Rotate JWT secret regularly
- [ ] Enable Vault audit logging
- [ ] Set up Vault backups
- [ ] Configure SSL/TLS for Vault
- [ ] Implement token refresh mechanism
- [ ] Add rate limiting to auth endpoints

## Troubleshooting

**Vault won't start:**
```bash
docker-compose -f docker-compose.vault.yml logs vault
```

**Can't connect to Vault:**
```bash
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='galani-dev-token'
vault status
```

**Secrets not found:**
```bash
# List all secrets
docker exec galani-vault vault kv list galani-secrets/

# Read specific secret
docker exec galani-vault vault kv get galani-secrets/openai/api_key
```
