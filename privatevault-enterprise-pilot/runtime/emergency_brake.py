import json
import os


def set_safety_threshold(threshold):
    config = {
        "max_gradient": threshold,
        "status": "LOCKED" if threshold <= 0 else "ACTIVE",
    }
    with open("policy_config.json", "w") as f:
        json.dump(config, f)
    print(f"🛑 EMERGENCY POLICY UPDATED: Max Gradient is now {threshold}")
    print("⚖️ All OAAS actions above this limit will be BLOCKED.")


if __name__ == "__main__":
    import sys

    val = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
    set_safety_threshold(val)
