#!/usr/bin/env python3
"""
Migrate API keys from api_keys.json to Vault
RUN THIS ONCE, then delete api_keys.json
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.secrets.secrets_manager import get_secrets_manager

def migrate_api_keys():
    """Migrate API keys from JSON file to Vault"""
    
    # Read existing api_keys.json
    try:
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)
    except FileNotFoundError:
        print("❌ api_keys.json not found")
        return False
    
    # Get secrets manager
    secrets = get_secrets_manager()
    
    # Migrate each key
    for service, key_data in api_keys.items():
        path = f"{service}/api_key"
        print(f"Migrating {service}...")
        
        secrets.set_secret(path, key_data)
        print(f"✅ Migrated {service}")
    
    print("\n✅ All API keys migrated to Vault")
    print("\n⚠️  NEXT STEPS:")
    print("1. Verify keys in Vault: docker exec -it galani-vault vault kv list galani-secrets/")
    print("2. Update your code to use secrets_manager.get_secret()")
    print("3. DELETE api_keys.json: rm api_keys.json")
    print("4. Commit changes: git add -A && git commit -m 'SECURITY: Moved API keys to Vault'")
    
    return True

if __name__ == "__main__":
    migrate_api_keys()
