import sys
import os

# Shadow mode flag (default: ON)
SHADOW_MODE = os.getenv("UAAL_SHADOW_MODE", "true").lower() == "true"

TEST_INTENT = {
    "action": "transfer_money",
    "amount": 250000,
    "jurisdiction": "IN"
}

def evaluate(intent):
    if intent["amount"] > 100000:
        return "BLOCK"
    return "ALLOW"

decision = evaluate(TEST_INTENT)

print(f"UAAL CI DECISION: {decision}")
print(f"UAAL SHADOW MODE: {SHADOW_MODE}")

# Always write decision to file for later steps
with open("uaal_decision.txt", "w") as f:
    f.write(decision)

if decision != "ALLOW" and not SHADOW_MODE:
    print("❌ POLICY VIOLATION — BUILD BLOCKED")
    sys.exit(1)

if decision != "ALLOW" and SHADOW_MODE:
    print("⚠️ POLICY VIOLATION — SHADOW MODE (BUILD ALLOWED)")

print("✅ UAAL CHECK COMPLETE")
sys.exit(0)
