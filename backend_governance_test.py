import requests
import json
import time

ENGINE = "http://127.0.0.1:8000"
GATEWAY = "http://127.0.0.1:8001"

def test_health():
    r = requests.get(f"{ENGINE}/health")
    assert r.status_code == 200
    print("✅ Engine Healthy")

def test_ai_action():
    payload = {
        "prompt": "List files in /home directory",
        "action": "file_read:/home; external_api_call:https://api.example.com"
    }

    r = requests.post(f"{ENGINE}/execute", json=payload)

    if r.status_code != 200:
        print("❌ Execution Blocked (Policy)")
        return None

    data = r.json()
    print("✅ Action Executed")
    return data

def test_drift():
    r = requests.get(f"{ENGINE}/drift/latest")

    if r.status_code != 200:
        print("⚠️ No drift endpoint")
        return

    data = r.json()

    print("📊 Alignment Score:", data["alignment_score"])
    print("🚦 Blocked:", data["should_block"])

def test_evidence():
    try:
        with open("proof.json") as f:
            proof = json.load(f)

        print("🔐 Evidence Found")
        print("Intent Hash:", proof["analyses"][0]["coreIntentHash"])
        print("Risk Level:", proof["analyses"][0]["riskLevel"])

    except:
        print("❌ No Evidence Found")


if __name__ == "__main__":

    print("\n=== PRIVATEVAULT BACKEND TEST ===\n")

    test_health()
    time.sleep(1)

    result = test_ai_action()
    time.sleep(1)

    test_drift()
    time.sleep(1)

    test_evidence()

    print("\n✅ TEST COMPLETE\n")
