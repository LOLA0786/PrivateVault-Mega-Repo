import hashlib, json, time

class LineageLedger:
    def __init__(self, log_path="/tmp/audit_chain.jsonl"):
        self.log_path = log_path
        self.prev_hash = "0000000000"

    def sign_decision(self, decision_data):
        nonce = str(time.time_ns())
        content = f"{decision_data['action']}{decision_data['user']}{nonce}{self.prev_hash}"
        current_hash = hashlib.sha256(content.encode()).hexdigest()
        
        record = {
            "lineage_id": decision_data['decision_id'],
            "user": decision_data['user'],
            "action": decision_data['action'],
            "hash": current_hash,
            "prev_hash": self.prev_hash,
            "nonce": nonce,
            "timestamp": time.time()
        }
        
        with open(self.log_path, "a") as f:
            f.write(json.dumps(record) + "\n")
            
        self.prev_hash = current_hash
        return current_hash
