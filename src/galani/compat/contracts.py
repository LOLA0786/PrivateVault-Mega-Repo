"""
Compat contracts for tests/demos.

Goal:
- Preserve production engine contracts.
- Provide stable test-friendly wrappers for legacy test suite.

Only tests should import/monkeypatch these.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import json
import hashlib
import time

# Import real core engine
from galani.core import policy_engine as real_policy_engine


def _stable_json(obj: Any) -> str:
    """Stable JSON encoding for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def authorize_intent(action: str, principal: Optional[dict] = None, context: Optional[dict] = None,
                    policy_version: str = "v4", mode: str = "enforce", **kwargs) -> Dict[str, Any]:
    """
    Test-friendly wrapper.

    Tests call:
        authorize_intent(action:str, principal:dict, context:dict)

    Production engine expects an enveloped payload. We translate.
    """
    principal = principal or {}
    context = context or {}

    # Build enveloped intent expected by real engine
    enveloped = {
        "action": str(action),
        "principal": principal,
        "context": context,
        "policy_version": policy_version,
        "mode": mode,
    }

    decision = real_policy_engine.authorize_intent(enveloped)

    # Some real implementations return bool; normalize.
    if isinstance(decision, bool):
        decision_obj = {
            "allowed": bool(decision),
            "action": str(action),
            "policy_version": policy_version,
            "context": context,
        }
    elif isinstance(decision, dict):
        decision_obj = decision
        decision_obj.setdefault("allowed", False)
        decision_obj.setdefault("action", str(action))
        decision_obj.setdefault("policy_version", policy_version)
        decision_obj.setdefault("context", context)
    else:
        decision_obj = {
            "allowed": False,
            "action": str(action),
            "policy_version": policy_version,
            "context": context,
            "reason": f"unexpected decision type: {type(decision)}",
        }

    # Ensure required keys expected by regression tests
    decision_obj.setdefault("reason", "allowed" if decision_obj["allowed"] else "denied")
    decision_obj.setdefault("mode", mode)

    return decision_obj


def authorize_enveloped_intent(enveloped: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    If tests pass enveloped intent already.
    """
    if not isinstance(enveloped, dict):
        return {"allowed": False, "reason": "invalid enveloped intent"}

    action = str(enveloped.get("action", "unknown"))
    principal = enveloped.get("principal") or {}
    context = enveloped.get("context") or {}
    policy_version = enveloped.get("policy_version", "v4")
    mode = enveloped.get("mode", "enforce")

    return authorize_intent(action, principal, context, policy_version=policy_version, mode=mode)


def generate_evidence(intent: Dict[str, Any], decision: Dict[str, Any], policy_version: Optional[str] = None) -> Dict[str, Any]:
    """
    Regression tests expect:
      evidence["decision"] -> bool
      evidence["policy_version"] -> string
      evidence["evidence_hash"] -> string
      evidence["timestamp"] -> float or int

    We do NOT alter production evidence module. This is compat.
    """
    policy_version = policy_version or decision.get("policy_version") or intent.get("policy_version") or "unknown"

    # Ensure decision bool normalization
    allowed = decision["allowed"] if isinstance(decision, dict) and "allowed" in decision else bool(decision)

    ts = time.time()

    payload = {
        "intent": intent,
        "decision": {"allowed": allowed, "action": intent.get("action"), "policy_version": policy_version},
        "policy_version": policy_version,
    }

    # Evidence hash must ignore timestamp for determinism tests
    evidence_hash = hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()

    return {
        "intent": intent,
        "decision": allowed,
        "policy_version": policy_version,
        "evidence_hash": evidence_hash,
        "timestamp": ts,
    }


def verify_evidence(intent: Dict[str, Any], decision: Dict[str, Any], policy_version: str, evidence_hash: str) -> bool:
    """
    Tests call: verify_evidence(intent, decision, policy_version, evidence_hash)

    Validate deterministically.
    """
    expected = generate_evidence(intent, decision, policy_version=policy_version)["evidence_hash"]
    return expected == evidence_hash

# ---- PV_FORCE_VERIFY_REDIRECT ----
try:
    from evidence import verify_evidence as _pv_verify_evidence
    def verify_evidence(*args, **kwargs):
        return _pv_verify_evidence(*args, **kwargs)
except Exception:
    pass
# ---- /PV_FORCE_VERIFY_REDIRECT ----
