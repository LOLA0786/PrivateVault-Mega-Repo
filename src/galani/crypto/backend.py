class CryptoBackend:
    name = "base"

    def sign(self, data: bytes) -> bytes:
        raise NotImplementedError

    def verify(self, data: bytes, signature: bytes) -> bool:
        raise NotImplementedError
