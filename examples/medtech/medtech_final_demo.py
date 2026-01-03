from execute_and_log import execute_and_log

def run_medtech_intent(payload):
    intent = {
        "domain": "medtech",
        "actor": "demo-agent",
        "action": payload.get("action", "unknown"),
        "patient_age": payload.get("patient_age", 99),
        "medicine": payload.get("medicine"),
        "mode": payload.get("mode", "ENFORCE"),
    }
    return execute_and_log(intent)
