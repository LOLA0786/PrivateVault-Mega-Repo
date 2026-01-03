import requests

def run_test(name, mode, gradient, is_encrypted=False):
    status = "🔒" if is_encrypted else "🔓"
    print(f"\n📡 [TEST: {name}] | Mode: {mode} | Gradient: {gradient} | {status}")
    url = "http://127.0.0.1:8001/secure_optimize"
    payload = {
        "current_val": 100.0, 
        "raw_gradient": gradient, 
        "mode": mode, 
        "actor": "galani_founder",
        "is_encrypted": is_encrypted
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AUTHORIZED | 🔑 SIG: {data['evidence_hash'][:15]}...")
        else:
            print(f"🛑 BLOCKED: {response.status_code} - {response.json().get('detail')}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 INITIATING PRIVACY-FIRST SOVEREIGN TEST...")
    # Standard Transparent Tests
    run_test("HIGH_RISK_SHADOW", "SHADOW", 99.9, is_encrypted=False)
    # Federated Privacy Test (The new feature!)
    run_test("PRIVATE_FEDERATED_SAFE", "ENFORCE", 0.05, is_encrypted=True)
    # Blocked Enforce Test
    run_test("HIGH_RISK_ENFORCE", "ENFORCE", 99.9, is_encrypted=False)
