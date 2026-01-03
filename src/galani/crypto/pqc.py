from .interfaces import PQCKeyExchange

class KyberKEM(PQCKeyExchange):
    def __init__(self):
        try:
            from pqcrypto.kem import kyber512
            self._kyber = kyber512
            self.public_key, self.secret_key = kyber512.generate_keypair()
        except Exception as e:
            raise RuntimeError(
                "Kyber PQC backend not available on this platform. "
                "Install a supported pqcrypto build or use HSM/KMS-backed PQC."
            ) from e

    def encapsulate(self):
        ciphertext, shared_secret = self._kyber.encrypt(self.public_key)
        return {"ciphertext": ciphertext, "shared_secret": shared_secret}

    def decapsulate(self, ciphertext: bytes) -> bytes:
        return self._kyber.decrypt(ciphertext, self.secret_key)
