from typing import List
from .decision_record import DecisionRecord
import hashlib


class AuditChain:
    def __init__(self):
        self.chain: List[str] = []

    def append(self, record: DecisionRecord) -> str:
        prev = self.chain[-1] if self.chain else "GENESIS"
        combined = prev + record.hash()
        root = hashlib.sha256(combined.encode()).hexdigest()
        self.chain.append(root)
        return root

    def verify(self) -> bool:
        return len(self.chain) == len(set(self.chain))
