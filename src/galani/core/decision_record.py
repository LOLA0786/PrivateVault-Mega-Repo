import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class DecisionRecord:
    intent_hash: str
    policy_version: str
    regulatory_snapshot: str
    decision: bool
    risk_score: float
    timestamp: str

    def hash(self) -> str:
        payload = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()
