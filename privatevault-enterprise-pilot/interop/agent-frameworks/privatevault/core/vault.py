import json, os, time, hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

@dataclass
class VaultEvent:
    ts: str
    framework: str
    event_type: str
    payload: Dict[str, Any]
    payload_hash: str
    chain_hash: str

class PrivateVault:
    def __init__(self, out_dir: str = "privatevault/reports/evidence", run_id: Optional[str] = None):
        os.makedirs(out_dir, exist_ok=True)
        self.out_dir = out_dir
        self.run_id = run_id or time.strftime("%Y%m%d_%H%M%S", time.gmtime())
        self.filepath = os.path.join(out_dir, f"pv_trace_{self.run_id}.jsonl")
        self._last_chain = "GENESIS"

    def record(self, framework: str, event_type: str, payload: Dict[str, Any]) -> VaultEvent:
        ts = _now()
        raw = json.dumps({"ts": ts, "framework": framework, "event_type": event_type, "payload": payload}, sort_keys=True).encode()
        payload_hash = _sha256(raw)
        chain_hash = _sha256((self._last_chain + payload_hash).encode())
        self._last_chain = chain_hash

        evt = VaultEvent(ts=ts, framework=framework, event_type=event_type,
                         payload=payload, payload_hash=payload_hash, chain_hash=chain_hash)

        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(evt.__dict__, sort_keys=True) + "\n")
        return evt
