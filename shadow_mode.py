"""
Shadow mode evaluation with metrics capture.
"""

SHADOW_METRICS = {
    "divergence_count": 0,
    "prevented_total": 0.0,
    "high_risk_examples": [],
}


def shadow_evaluate(intent: dict):
    amount = float(intent.get("amount", 0))
    intent_hash = intent.get("intent_hash")

    shadow_decision = {"allowed": True, "policy": "SHADOW_NONE"}

    # Stricter shadow policy
    if intent.get("domain") == "fintech" and amount >= 20000:
        shadow_decision = {"allowed": False, "policy": "SHADOW_FINTECH_STRICT"}

        SHADOW_METRICS["divergence_count"] += 1
        SHADOW_METRICS["prevented_total"] += amount

        if amount > 10000:
            SHADOW_METRICS["high_risk_examples"].append(
                {
                    "amount": amount,
                    "intent_hash": intent_hash,
                    "policy": shadow_decision["policy"],
                }
            )

    return shadow_decision


def shadow_summary():
    return SHADOW_METRICS
