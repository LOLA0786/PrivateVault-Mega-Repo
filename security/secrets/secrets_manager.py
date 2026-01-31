import os

# Optional Vault support
try:
    import hvac
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False


class EnvSecretsManager:
    """Fallback secrets manager using env vars"""

    def get(self, key: str, default=None):
        return os.getenv(key, default)


def get_secrets_manager():
    """
    Returns Vault client if available, otherwise env-based manager
    """

    if VAULT_AVAILABLE and os.getenv("VAULT_ADDR"):
        client = hvac.Client(
            url=os.getenv("VAULT_ADDR"),
            token=os.getenv("VAULT_TOKEN"),
        )

        if not client.is_authenticated():
            raise RuntimeError("Vault authentication failed")

        return client

    # Fallback (demo-safe)
    return EnvSecretsManager()
