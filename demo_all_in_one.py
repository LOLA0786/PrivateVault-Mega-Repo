"""
UAAL FULL SYSTEM DEMO
====================
One file. One run. All core features.
"""

import time
import uuid
import hashlib
import json


# -----------------------------
# POLICY ENGINE (AUTHORITATIVE)
# -----------------------------

def authorize_intent(intent: dict):
    action = intent.get("action")
    args = intent.get("args", {})
    context = intent.get("context", {})

    evidence_id = str(uuid.uuid4())
    timestamp = int(time.time())

    # FinTech invariant
    if action == "transfer_money":
        amount = args.get("amount", 0)
        jurisdiction = context.get("jurisdiction")

        if jurisdiction == "IN" and amount >= 100000:
            return decision_payload(
                False,
                "High-value transfer blocked by policy",
                "fintech-v1.0",
                intent,
                evidence_id,
                timestamp
            )

    # MedTech invariant
    if action == "prescribe_medication":
        if context.get("patient_age", 0) < 18 and not context.get("consent", False):
            return decision_payload(
                False,
                "Minor prescription without consent",
                "medtech-v1.0",
                intent,
                evidence_id,
                timestamp
            )

    return decision_payload(
        True,
        "Allowed by policy",
        "default-v1.0",
        intent,
        evidence_id,
        timestamp
    )


# -----------------------------
# EVIDENCE + AUDIT
# -----------------------------

AUDIT_LOG = {}


def decision_payload(allowed, reason, policy_version, intent, evidence_id, timestamp):
    payload = {
        "allowed": allowed,
        "decision": "ALLOW" if allowed else "BLOCK",
        "reason": reason,
        "policy_version": policy_version,
        "intent": intent,
        "evidence_id": evidence_id,
        "timestamp": timestamp,
    }

    payload["evidence_hash"] = hash_payload(payload)
    AUDIT_LOG[evidence_id] = payload
    return payload


def hash_payload(payload: dict):
    canonical = json.dumps(payload, sort_keys=True).encode()
    return hashlib.sha256(canonical).hexdigest()


def replay_evidence(evidence_id: str):
    stored = AUDIT_LOG.get(evidence_id)
    if not stored:
        return {"valid": False, "reason": "Evidence not found"}

    recomputed = hash_payload(stored)
    return {
        "valid": recomputed == stored["evidence_hash"],
        "evidence_id": evidence_id,
        "policy_version": stored["policy_version"]
    }


# -----------------------------
# AGENT (SIMULATED / LLM-LIKE)
# -----------------------------

def agent_proposes(action, args, context):
    print(f"\n🤖 Agent proposes: {action}")
    return {
        "agent_id": "demo-agent",
        "action": action,
        "args": args,
        "context": context
    }


# -----------------------------
# FULL DEMO RUN
# -----------------------------

def run_demo():
    print("\n==============================")
    print(" UAAL FULL SYSTEM DEMO START ")
    print("==============================")

    # FinTech BLOCK
    intent1 = agent_proposes(
        "transfer_money",
        {"amount": 250000},
        {"jurisdiction": "IN"}
    )
    decision1 = authorize_intent(intent1)
    print("Decision:", decision1["decision"])
    print("Evidence ID:", decision1["evidence_id"])

    replay1 = replay_evidence(decision1["evidence_id"])
    print("Replay valid:", replay1["valid"])

    # FinTech ALLOW
    intent2 = agent_proposes(
        "transfer_money",
        {"amount": 25000},
        {"jurisdiction": "IN"}
    )
    decision2 = authorize_intent(intent2)
    print("Decision:", decision2["decision"])
    print("Evidence ID:", decision2["evidence_id"])

    # MedTech BLOCK
    intent3 = agent_proposes(
        "prescribe_medication",
        {"drug": "morphine"},
        {"patient_age": 14, "consent": False}
    )
    decision3 = authorize_intent(intent3)
    print("Decision:", decision3["decision"])
    print("Evidence ID:", decision3["evidence_id"])

    replay3 = replay_evidence(decision3["evidence_id"])
    print("Replay valid:", replay3["valid"])

    print("\n==============================")
    print(" UAAL DEMO COMPLETE ")
    print("==============================\n")


if __name__ == "__main__":
    run_demo()
