import httpx
import asyncio


async def demo_scenario(name, gradient, mode):
    print(f"\n--- Scenario: {name} (Mode: {mode}) ---")
    payload = {
        "current_val": 100.0,
        "raw_gradient": gradient,
        "mode": mode,
        "actor": "governed_gateway",
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post("http://localhost:8001/secure_optimize", json=payload)
            print(f"Status: {r.status_code}")
            print(f"Response: {r.json()}")
        except Exception as e:
            print(f"Error: {e}")


async def main():
    # 1. Safe Shadow (Should log ALLOW but not strictly block)
    await test_scenario("SAFE_SHADOW", 0.01, "SHADOW")

    # 2. Risk Enforce (Should BLOCK)
    await test_scenario("HIGH_RISK_ENFORCE", 99.9, "ENFORCE")


if __name__ == "__main__":
    asyncio.run(main())
