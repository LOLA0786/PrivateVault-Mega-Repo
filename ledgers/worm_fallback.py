import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from .ledger_base import LedgerBase

UTC = timezone.utc
GENESIS_HASH = "0" * 64


class WORMFallback(LedgerBase):
    def __init__(self):
        self.records = []
        self.log_path = self._resolve_log_path()
        self.previous_hash = GENESIS_HASH
        self._load_existing()

    async def submit_audit(self, intent: Dict[str, Any], decision: Dict[str, Any], user_id: str) -> str:
        timestamp = datetime.now(UTC).isoformat()
        audit = {
            "intent": intent,
            "decision": decision,
            "user_id": user_id,
            "timestamp": timestamp,
        }
        entry = {
            "index": len(self.records),
            "timestamp": timestamp,
            "audit": audit,
            "previous_hash": self.previous_hash,
        }
        entry_hash = self._hash_entry(entry)
        entry["hash"] = entry_hash
        self._append_entry(entry)
        return entry_hash

    async def query_chain(self, id_: str) -> Dict[str, Any]:
        for entry in self.records:
            if entry.get("hash") == id_:
                return entry.get("audit", {})
        return {}

    def write(self, data: Dict[str, Any]) -> None:
        # Backwards-compatible helper
        entry = {
            "index": len(self.records),
            "timestamp": datetime.now(UTC).isoformat(),
            "audit": {"data": data},
            "previous_hash": self.previous_hash,
        }
        entry_hash = self._hash_entry(entry)
        entry["hash"] = entry_hash
        self._append_entry(entry)

    def read_all(self):
        return self.records

    def _resolve_log_path(self) -> str:
        storage_root = os.getenv("PV_STORAGE_PATH", "/tmp")
        os.makedirs(storage_root, exist_ok=True)
        return os.path.join(storage_root, "worm_ledger.jsonl")

    def _hash_entry(self, entry: Dict[str, Any]) -> str:
        canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _append_entry(self, entry: Dict[str, Any]) -> None:
        self.records.append(entry)
        self.previous_hash = entry["hash"]
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _load_existing(self) -> None:
        if not os.path.exists(self.log_path):
            open(self.log_path, "a").close()
            return
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                self.records.append(entry)
                self.previous_hash = entry.get("hash", self.previous_hash)
