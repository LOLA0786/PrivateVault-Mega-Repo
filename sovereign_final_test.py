import httpx
import asyncio
import json

async def run_test(name, gradient, mode):
    print(f"\n📡 [TEST: {name}] | Mode: {mode} | Gradient: {gradient}")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post("http://127.0.0.1:8001/secure_optimize", 
                                json={"current_val": 100.0, "raw_gradient": gradient, "mode": mode, "actor": "mumbai_founder"})
            
            if r.status_code == 200:
                print(f"✅ AUTHORIZED: {r.json()['optimized_value']}")
                print(f"🔑 KERNEL_SIG: {r.json()['evidence_hash'][:20]}...")
            else:
                print(f"🛑 BLOCKED: {r.status_code} - {r.json()['detail']}")
        except Exception as e:
            print(f"❌ CONNECTION ERROR: {e}")

async def main():
    print("🚀 INITIATING SOVEREIGN CORE TEST...")
    # Test 1: High Risk in Shadow Mode (Should be allowed but logged)
    await run_test("HIGH_RISK_SHADOW", 99.9, "SHADOW")
    
    # Test 2: High Risk in Enforce Mode (Should be HARD BLOCKED)
    await run_test("HIGH_RISK_ENFORCE", 99.9, "ENFORCE")
    
    # Test 3: Safe optimization
    await run_test("SAFE_ENFORCE", 0.05, "ENFORCE")

if __name__ == "__main__":
    asyncio.run(main())
