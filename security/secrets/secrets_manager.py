"""
Production-grade secrets management with HashiCorp Vault
"""
import os
import hvac
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class SecretsManager:
    """Centralized secrets management"""
    
    def __init__(self):
        vault_addr = os.getenv('VAULT_ADDR', 'http://localhost:8200')
        vault_token = os.getenv('VAULT_TOKEN', 'galani-dev-token')
        
        self.client = hvac.Client(url=vault_addr, token=vault_token)
        
        if not self.client.is_authenticated():
            raise Exception("Failed to authenticate with Vault")
        
        logger.info("Successfully connected to Vault")
    
    def get_secret(self, path: str) -> Optional[Dict]:
        """
        Retrieve secret from Vault
        
        Example:
            secret = secrets_manager.get_secret('openai/api_key')
            api_key = secret['data']['key']
        """
        try:
            secret = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point='galani-secrets'
            )
            logger.info(f"Retrieved secret: {path}")
            return secret
        except Exception as e:
            logger.error(f"Failed to retrieve secret {path}: {e}")
            return None
    
    def set_secret(self, path: str, secret_data: Dict):
        """
        Store secret in Vault
        
        Example:
            secrets_manager.set_secret('openai/api_key', {'key': 'sk-...'})
        """
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secret_data,
                mount_point='galani-secrets'
            )
            logger.info(f"Stored secret: {path}")
        except Exception as e:
            logger.error(f"Failed to store secret {path}: {e}")
            raise

# Singleton instance
_secrets_manager = None

def get_secrets_manager() -> SecretsManager:
    """Get or create secrets manager instance"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager
