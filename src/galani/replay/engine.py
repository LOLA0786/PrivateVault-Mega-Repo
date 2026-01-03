import hashlib
import json
import time
from typing import Dict

class DecisionReplayEngine:
    def __init__(self):
        self._store = {}

    def record(self, decision_id: str, payload: Dict):
        payload["timestamp"] = time.time()
        payload["hash"] = self._hash(payload)
        self._store[decision_id] = payload

    def replay(self, decision_id: str) -> Dict:
        return self._store[decision_id]

    def _hash(self, payload: Dict) -> str:
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()
