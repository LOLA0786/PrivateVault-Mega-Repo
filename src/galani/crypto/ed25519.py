from nacl.signing import SigningKey
from nacl.exceptions import BadSignatureError
from .interfaces import SignatureEngine

class Ed25519Signer(SignatureEngine):
    def __init__(self, private_key: bytes | None = None):
        self.signing_key = SigningKey(private_key) if private_key else SigningKey.generate()
        self.verify_key = self.signing_key.verify_key

    def sign(self, payload: bytes) -> bytes:
        return self.signing_key.sign(payload).signature

    def verify(self, payload: bytes, signature: bytes) -> bool:
        try:
            self.verify_key.verify(payload, signature)
            return True
        except BadSignatureError:
            return False
