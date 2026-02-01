import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"


def pretty(r):
    print(json.dumps(r, indent=2))


def ingest_intent():
    payload = {
        "intent_id": "test_user_intent_001",
        "actor": "user_alice",
        "domain": "fintech",
        "raw_input": "I want to transfer 50000 INR to a new beneficiary",
        "normalized_intent": {
            "action": "transfer_funds",
            "amount": 50000,
            "currency": "INR",
            "beneficiary": "new",
        },
        "confidence": 0.42,
        "timestamp": datetime.utcnow().isoformat(),
    }

    r = requests.post(f"{BASE_URL}/intent/ingest", json=payload)
    print("\n--- INGEST INTENT ---")
    pretty(r.json())


def add_event(strength):
    payload = {
        "intent_id": "test_user_intent_001",
        "event_type": "reinforcement",
        "strength": strength,
        "timestamp": datetime.utcnow().isoformat(),
    }

    r = requests.post(f"{BASE_URL}/intent/event", json=payload)
    print(f"\n--- ADD EVENT (strength={strength}) ---")
    pretty(r.json())


def fetch_intent():
    r = requests.get(f"{BASE_URL}/intent/test_user_intent_001")
    print("\n--- FETCH INTENT STATE ---")
    pretty(r.json())


def replay_intent():
    payload = {"intent_id": "test_user_intent_001", "mode": "deterministic"}

    r = requests.post(f"{BASE_URL}/intent/replay", json=payload)
    print("\n--- REPLAY INTENT ---")
    pretty(r.json())


if __name__ == "__main__":
    ingest_intent()
    time.sleep(0.5)

    add_event(0.6)
    time.sleep(0.5)

    add_event(0.85)
    time.sleep(0.5)

    fetch_intent()
    replay_intent()
