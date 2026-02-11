from typing import Any, Dict
from enum import Enum


class GovernanceMode(str, Enum):
    STRICT = "STRICT"
    RELAXED = "RELAXED"
    DEMO = "DEMO"


VALID_DECISIONS = {"ALLOW", "BLOCK", "REVIEW"}


# ---------------------------------------------------
# 1️⃣ Input Normalizer (Used by API routes)
# ---------------------------------------------------

def normalize(payload: Dict) -> Dict:
    """
    Normalize incoming data into canonical format.
    Used by API routes.
    """

    if not isinstance(payload, dict):
        return {"text": str(payload)}

    text = (
        payload.get("text")
        or payload.get("message")
        or payload.get("input")
        or ""
    )

    return {
        "source": payload.get("source", "unknown"),
        "sender": payload.get("sender", "unknown"),
        "text": text.strip(),
    }


# ---------------------------------------------------
# 2️⃣ Governance Output Normalizer (Used by tests)
# ---------------------------------------------------

def _is_valid_payload(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False

    decision = payload.get("decision")
    confidence = payload.get("confidence")

    if decision not in VALID_DECISIONS:
        return False

    if not isinstance(confidence, (int, float)):
        return False

    return True


def normalize_ai_output(raw: Any, mode: GovernanceMode) -> Dict[str, Any]:
    # DEMO MODE — always block
    if mode == GovernanceMode.DEMO:
        return {
            "decision": "BLOCK",
            "raw_valid": False,
            "reason": "DEMO_MODE_ENFORCED",
        }

    is_valid = _is_valid_payload(raw)

    if is_valid:
        return {
            "decision": raw["decision"],
            "confidence": raw["confidence"],
            "raw_valid": True,
        }

    if mode == GovernanceMode.STRICT:
        return {
            "decision": "BLOCK",
            "raw_valid": False,
        }

    if mode == GovernanceMode.RELAXED:
        return {
            "decision": "REVIEW",
            "raw_valid": False,
        }

    return {
        "decision": "BLOCK",
        "raw_valid": False,
    }
