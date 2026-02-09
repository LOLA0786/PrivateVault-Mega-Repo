import json
from datetime import datetime

with open("synthetic_data/evidence_store.json") as f:
    evidence = json.load(f)

with open("synthetic_data/chat_responses.json") as f:
    templates = json.load(f)

def respond(request_id: str):
    evt = next(e for e in evidence if e["request_id"] == request_id)

    template = (
        templates["why_blocked"]["template"]
        if evt["decision"] == "BLOCK"
        else templates["why_allowed"]["template"]
    )

    return template.format(
        policy=evt["policy"],
        reason="Policy enforcement",
        hash=evt["hash"],
        timestamp=evt["timestamp"],
    )

if __name__ == "__main__":
    print(respond("req_1001"))
