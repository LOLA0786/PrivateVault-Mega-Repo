"""Immutable Decision Log Ledger"""
import json
import hashlib
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DecisionLedger:
    def __init__(self, log_file: str = "ai_firewall_ledger.jsonl"):
        self.log_file = log_file
        self.chain = []
        self.previous_hash = "0" * 64
    
    def _calculate_hash(self, entry: Dict) -> str:
        entry_str = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(entry_str.encode()).hexdigest()
    
    def log_interaction(self, event_type: str, data: Dict) -> Dict:
        entry = {
            "index": len(self.chain),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data,
            "previous_hash": self.previous_hash
        }
        
        current_hash = self._calculate_hash(entry)
        entry["hash"] = current_hash
        
        self.chain.append(entry)
        self.previous_hash = current_hash
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        logger.info(f"📝 Logged {event_type} #{entry['index']}")
        return entry
    
    def verify_chain_integrity(self) -> bool:
        previous = "0" * 64
        
        for idx, entry in enumerate(self.chain):
            if entry["previous_hash"] != previous:
                logger.error(f"❌ Chain broken at {idx}")
                return False
            
            entry_copy = entry.copy()
            stored_hash = entry_copy.pop("hash")
            calculated_hash = self._calculate_hash(entry_copy)
            
            if stored_hash != calculated_hash:
                logger.error(f"❌ Hash mismatch at {idx}")
                return False
            
            previous = stored_hash
        
        logger.info("✅ Chain integrity verified")
        return True

if __name__ == "__main__":
    ledger = DecisionLedger()
    
    print("\n" + "="*50)
    print("TEST: Logging Events")
    print("="*50)
    
    ledger.log_interaction("input_filter", {
        "user_id": "user_001",
        "threat_detected": False
    })
    
    ledger.log_interaction("input_filter", {
        "user_id": "user_002",
        "threat_detected": True,
        "reason": "Prompt injection"
    })
    
    print(f"\nTotal logs: {len(ledger.chain)}")
    print(f"Chain valid: {ledger.verify_chain_integrity()}")
