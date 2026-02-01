import httpx
import asyncio
import json

GATEWAY_URL = "http://localhost:8001/secure_optimize"


async def run_test(name, current_val, gradient):
    print(f"\n--- Testing Scenario: {name} ---")
    payload = {
        "current_val": current_val,
        "raw_gradient": gradient,
        "client_id": "test_agent_01",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(GATEWAY_URL, json=payload, timeout=10.0)
            result = resp.json()

            if resp.status_code == 200:
                print(f"✅ AUTHORIZED: {result['authorized_by']}")
                print(f"🔑 Evidence Hash: {result['evidence_hash'][:16]}...")
                print(f"🚀 OAAS Output: {result['optimized_value']:.4f}")
            else:
                print(f"❌ BLOCKED: {result['detail']}")
        except Exception as e:
            print(f"⚠️ Error: Ensure all services (UAAL & OAAS) are running. {e}")


async def main():
    # Scenario 1: Safe request (Low gradient)
    await run_test("Safe Optimization", 100.0, 0.05)

    # Scenario 2: High-risk request (Extreme gradient - triggers UAAL Block)
    await run_test("High-Risk Block", 100.0, 99.9)


if __name__ == "__main__":
    asyncio.run(main())
