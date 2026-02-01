from nacl.signing import SigningKey, VerifyKey
from .backend import CryptoBackend


class Ed25519Backend(CryptoBackend):
    name = "ed25519"

    def __init__(self):
        self._sk = SigningKey.generate()
        self._vk = self._sk.verify_key

    def sign(self, data: bytes) -> bytes:
        return self._sk.sign(data).signature

    def verify(self, data: bytes, signature: bytes) -> bool:
        try:
            self._vk.verify(data, signature)
            return True
        except Exception:
            return False
