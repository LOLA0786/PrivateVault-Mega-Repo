import json
from shadow_mode import shadow_evaluate

AUDIT_LOG = "audit.log"

def inspect():
    with open(AUDIT_LOG) as f:
        for line in f:
            record = json.loads(line)

            intent = {
                "domain": record["domain"],
                "amount": record.get("amount", 0),
            }

            real_allowed = record.get("allowed", True)

            shadow = shadow_evaluate(intent, real_allowed)

            record["shadow_decision"] = shadow
            record["shadow_diff"] = shadow["allowed"] != real_allowed

            print(record)

if __name__ == "__main__":
    inspect()
