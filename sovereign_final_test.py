import requests
import json

def run_test(name, mode, gradient):
    print(f"\n📡 [TEST: {name}] | Mode: {mode} | Gradient: {gradient}")
    url = "http://127.0.0.1:8001/secure_optimize"
    payload = {"current_val": 100.0, "raw_gradient": gradient, "mode": mode, "actor": "mumbai_founder"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AUTHORIZED: {data['optimized_value']}")
            print(f"🔑 KERNEL_SIG: {data['evidence_hash'][:20]}...")
        else:
            print(f"🛑 BLOCKED: {response.status_code} - {response.json().get('detail', 'Unknown Error')}")
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    print("🚀 INITIATING SOVEREIGN CORE TEST...")
    run_test("HIGH_RISK_SHADOW", "SHADOW", 99.9)
    run_test("HIGH_RISK_ENFORCE", "ENFORCE", 99.9)
    run_test("SAFE_ENFORCE", "ENFORCE", 0.05)
