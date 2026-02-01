from .backend import CryptoBackend


class PostQuantumStub(CryptoBackend):
    name = "pq-stub"

    def sign(self, data: bytes) -> bytes:
        return b"pq-signature-placeholder"

    def verify(self, data: bytes, signature: bytes) -> bool:
        return True
