import json

def replay(intent_hash):
    # Simulating a lookup in your PrivateVault state
    print(f"🔍 REPLAYING DECISION FOR: {intent_hash}")
    print("-" * 30)
    print("RESULT: BLOCK")
    print("REASON: Gradient exceeds Safety Threshold (1.0)")
    print("POLICY: sovereign-v1-finance")
    print("EVIDENCE: 0x8fa526d... (Verified)")

if __name__ == "__main__":
    replay("0xblocked001")
