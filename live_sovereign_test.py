import httpx
import asyncio

# The Conscience (Terminal 1)
UAAL_GATEWAY = "http://localhost:8000"
# The Muscle (Terminal 2)
OAAS_GATEWAY = "http://localhost:8001"

async def run_integration():
    print("\n🛡️  INITIATING SOVEREIGN STACK TEST...")
    async with httpx.AsyncClient() as client:
        # TEST 1: UAAL Direct Check
        try:
            uaal_health = await client.get(f"{UAAL_GATEWAY}/health")
            print(f"✅ UAAL (Conscience) is ONLINE: {uaal_health.status_code}")
        except Exception:
            print(f"❌ UAAL OFFLINE at {UAAL_GATEWAY}. Ensure Tab 1 is running.")
            return

        # TEST 2: Governed Execution (Safe)
        print("\n🚀 Scenario 1: Safe Optimization Request")
        payload = {"current_val": 100.0, "raw_gradient": 0.01}
        try:
            resp = await client.post(f"{OAAS_GATEWAY}/secure_optimize", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ SUCCESS: Decision Authorized by UAAL.")
                print(f"🔑 Evidence Hash: {data.get('evidence_hash', 'N/A')}")
                print(f"📊 OAAS Output: {data.get('optimized_value', 'N/A')}")
            else:
                print(f"⚠️  Blocked/Error: {resp.text}")
        except Exception as e:
            print(f"❌ OAAS Gateway OFFLINE at {OAAS_GATEWAY}. Ensure Tab 2 is running.")

if __name__ == "__main__":
    asyncio.run(run_integration())
