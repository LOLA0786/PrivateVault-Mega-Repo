from .ed25519 import Ed25519Backend
from .pq_fallback import PostQuantumStub


def get_crypto_backend():
    try:
        import pqcrypto  # noqa

        return PostQuantumStub()
    except Exception:
        return Ed25519Backend()
