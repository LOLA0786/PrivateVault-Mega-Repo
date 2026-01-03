def normalize_audit(entry):
    return {
        "timestamp": entry.get("timestamp"),
        "domain": entry.get("domain"),
        "actor": entry.get("actor", "demo-agent"),
        "action": entry.get("action"),
        "mode": entry.get("mode"),
        "decision": entry.get("decision"),
        "policy": entry.get("policy"),
        "intent_hash": entry.get("intent_hash"),
    }
