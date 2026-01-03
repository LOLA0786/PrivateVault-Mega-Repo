from abc import ABC, abstractmethod
from typing import Any, Dict

class ZKProver(ABC):
    @abstractmethod
    def prove_range(self, value: float, min_v: float, max_v: float) -> Dict[str, Any]:
        pass

class SignatureEngine(ABC):
    @abstractmethod
    def sign(self, payload: bytes) -> bytes:
        pass

    @abstractmethod
    def verify(self, payload: bytes, signature: bytes) -> bool:
        pass

class PQCKeyExchange(ABC):
    @abstractmethod
    def encapsulate(self) -> Dict[str, bytes]:
        pass

    @abstractmethod
    def decapsulate(self, ciphertext: bytes) -> bytes:
        pass
