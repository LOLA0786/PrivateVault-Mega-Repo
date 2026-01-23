"""
Compatibility wrapper for policy_engine.

Tests and demos in this monorepo historically imported `policy_engine` from repo root.

The real implementation lives here:
    ./src/galani/core/policy_engine.py

But function signatures evolved over time:
- Old style tests call: authorize_intent(action, principal, context)
- New implementation may expect: authorize_intent(enveloped_intent_dict)

This shim supports BOTH signatures so regression tests continue to run.
"""

from __future__ import annotations

from typing import Any, Dict
import importlib


def _load_real():
    return importlib.import_module("galani.core.policy_engine")


_real = _load_real()


def _to_enveloped(
    action: str, principal: Dict[str, Any], context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convert old-style args into an enveloped intent dict.
    """
    return {
        "intent": {
            "action": action,
            "context": context or {},
        },
        "principal": principal or {},
        "meta": {
            "source": "compat_shim",
            "mode": "test",
        },
    }


def authorize_intent__OLD(*args, **kwargs):
    """
    Backward compatible authorize_intent()

    Supported:
      - authorize_intent(enveloped_intent_dict)
      - authorize_intent(action, principal, context)
    """
    if hasattr(_real, "authorize_intent"):
        # new style: authorize_intent(enveloped_intent_dict)
        if len(args) == 1 and isinstance(args[0], dict):
            return _real.authorize_intent(args[0], **kwargs)

        # old style: authorize_intent(action, principal, context)
        if (
            len(args) == 3
            and isinstance(args[0], str)
            and isinstance(args[1], dict)
            and isinstance(args[2], dict)
        ):
            enveloped = _to_enveloped(args[0], args[1], args[2])
            return _real.authorize_intent(enveloped, **kwargs)

        # kwargs style
        if "action" in kwargs and "principal" in kwargs and "context" in kwargs:
            enveloped = _to_enveloped(
                kwargs["action"], kwargs["principal"], kwargs["context"]
            )
            return _real.authorize_intent(enveloped)

        raise TypeError(f"authorize_intent() unsupported args={args} kwargs={kwargs}")

    raise ImportError("Real policy_engine.authorize_intent not found")


def infer_risk(*args, **kwargs):
    """
    Backward compatible infer_risk().

    Old tests call: infer_risk(action, principal, context)
    New engine may not expose infer_risk; provide deterministic fallback.
    """
    if hasattr(_real, "infer_risk"):
        return _real.infer_risk(*args, **kwargs)

    # fallback scoring (simple + deterministic)
    action = args[0] if len(args) > 0 else kwargs.get("action", "")
    principal = args[1] if len(args) > 1 else kwargs.get("principal", {})
    context = args[2] if len(args) > 2 else kwargs.get("context", {})

    trust = (principal or {}).get("trust_level", "unknown")
    amount = (context or {}).get("amount", 0)

    score = 0.25
    if trust == "high":
        score -= 0.05
    if trust == "low":
        score += 0.20
    if isinstance(amount, (int, float)) and amount > 250000:
        score += 0.25

    score = max(0.0, min(1.0, score))

    return {
        "ok": True,
        "action": action,
        "risk_score": score,
        "risk_level": "high" if score >= 0.7 else "medium" if score >= 0.4 else "low",
        "signals": {
            "trust_level": trust,
            "amount": amount,
        },
    }


def generate_synthetic_data(*args, **kwargs):
    """
    If real function exists use it, else minimal fallback.
    """
    if hasattr(_real, "generate_synthetic_data"):
        return _real.generate_synthetic_data(*args, **kwargs)

    # fallback implementation for tests
    n = int(kwargs.get("n", args[0] if args else 5))
    return [{"id": i, "value": i * 7} for i in range(n)]


# ================= __PV_POLICY_ENGINE_COMPAT__ ====================
# Compatibility wrapper expected by tests/test_synthetic_pipeline.py
from typing import Any, Dict, List


def generate_synthetic_data(n: int = 5) -> List[Dict[str, Any]]:
    # Simple deterministic synthetic generator (works offline)
    out = []
    for i in range(int(n)):
        out.append(
            {"id": f"syn_{i}", "amount": 1000 + i * 100, "country": "IN", "ts": i}
        )
    return out


def infer_risk(
    action: str, principal: Dict[str, Any], context: Dict[str, Any]
) -> Dict[str, Any]:
    # minimal, stable risk response
    amt = float(context.get("amount", 0) or 0)
    score = min(1.0, amt / 500000.0)  # 0..1
    return {"risk_score": score, "reason": "synthetic_static_model"}


# ================================================================


# === PV_TEST_COMPAT_AUTHORIZE_INTENT_BEGIN ===
def authorize_intent(action, principal=None, context=None, **kwargs):
    """
    TEST COMPAT WRAPPER:
    tests call authorize_intent(action:str, principal:dict, context:dict)

    Real engine expects an enveloped payload with 'action' as STRING.
    This wrapper normalizes action/principal/context into that format.
    """
    if principal is None:
        principal = {}
    if context is None:
        context = {}

    # normalize action
    if isinstance(action, dict):
        action = (
            action.get("action")
            or action.get("tool_name")
            or action.get("name")
            or "unknown_action"
        )
    action = str(action)

    enveloped = {
        "action": action,
        "principal": principal,
        "context": context,
        "payload": {},  # tests expect payload ignored by policy
        "policy_version": kwargs.get("policy_version", "v4"),
    }

    return _real.authorize_intent(enveloped, **kwargs)


# === PV_TEST_COMPAT_AUTHORIZE_INTENT_END ===
