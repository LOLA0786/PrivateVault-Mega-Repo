from execute_and_log import execute_and_log

def run_fintech_intent(payload):
    intent = {
        "domain": "fintech",
        "actor": "demo-agent",
        "action": payload.get("action", "unknown"),
        "amount": payload.get("amount", 0),
        "beneficiary": payload.get("beneficiary"),
        "mode": payload.get("mode", "ENFORCE"),
    }
    return execute_and_log(intent)
