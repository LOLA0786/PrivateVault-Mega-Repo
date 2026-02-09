from enum import Enum
from typing import Any, Dict


class GovernanceMode(str, Enum):
    STRICT = "STRICT"
    RELAXED = "RELAXED"
    DEMO = "DEMO"


ALLOWED_DECISIONS = {"ALLOW", "BLOCK", "REVIEW"}


def normalize_ai_output(
    raw_output: Any,
    mode: GovernanceMode = GovernanceMode.STRICT,
) -> Dict[str, Any]:
    """
    Normalize untrusted AI output into a strict, safe contract.

    This function MUST NEVER throw.
    """

    # DEMO mode: deterministic, no randomness allowed
    if mode == GovernanceMode.DEMO:
        return {
            "decision": "BLOCK",
            "confidence": 1.0,
            "reason": "DEMO_MODE_ENFORCED",
            "raw_valid": True,
        }

    # If AI returned something totally unusable
    if not isinstance(raw_output, dict):
        return _fail("INVALID_OUTPUT_TYPE", raw_output, mode)

    decision = raw_output.get("decision")
    confidence = raw_output.get("confidence")

    # Decision must be explicit and valid
    if decision not in ALLOWED_DECISIONS:
        return _fail("INVALID_DECISION", raw_output, mode)

    # Confidence must be numeric and sane
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        return _fail("INVALID_CONFIDENCE", raw_output, mode)

    return {
        "decision": decision,
        "confidence": float(confidence),
        "reason": raw_output.get("reason", "AI_OUTPUT"),
        "raw_valid": True,
    }


def _fail(reason: str, raw_output: Any, mode: GovernanceMode) -> Dict[str, Any]:
    """
    Failure handling depends on governance mode.
    """

    if mode == GovernanceMode.RELAXED:
        return {
            "decision": "REVIEW",
            "confidence": 0.0,
            "reason": reason,
            "raw_valid": False,
        }

    # STRICT mode default
    return {
        "decision": "BLOCK",
        "confidence": 0.0,
        "reason": reason,
        "raw_valid": False,
    }
