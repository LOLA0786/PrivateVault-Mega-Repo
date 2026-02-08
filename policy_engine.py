"""
Standalone-compatible policy engine wrapper.

Uses galani engine if present.
Falls back to internal logic if not.
"""

from typing import Any, Dict, List
import importlib


# ======================
# Load real engine (if any)
# ======================

def _load_real():
    try:
        return importlib.import_module("galani.core.policy_engine")
    except ImportError:
        return None


_real = _load_real()


# ======================
# Fallback logic
# ======================

def _fallback_authorize(action, principal, context):

    trust = (principal or {}).get("trust_level", "unknown")
    amount = float((context or {}).get("amount", 0) or 0)

    allowed = True

    if trust == "low" and amount > 300000:
        allowed = False

    return {
        "allowed": allowed,
        "policy": "fallback_v1",
        "reason": "local_policy_engine",
    }


def _fallback_risk(action, principal, context):

    amt = float((context or {}).get("amount", 0) or 0)

    score = min(1.0, amt / 500000.0)

    return {
        "risk_score": score,
        "risk_level": "high" if score > 0.7 else "medium" if score > 0.4 else "low",
        "model": "fallback_static",
    }


# ======================
# Public API
# ======================

def authorize_intent(action, principal=None, context=None, **kwargs):

    if principal is None:
        principal = {}
    if context is None:
        context = {}

    # Use real engine if available
    if _real and hasattr(_real, "authorize_intent"):

        enveloped = {
            "action": str(action),
            "principal": principal,
            "context": context,
            "policy_version": kwargs.get("policy_version", "v1"),
        }

        return _real.authorize_intent(enveloped, **kwargs)

    # Fallback
    return _fallback_authorize(action, principal, context)


def infer_risk(action, principal=None, context=None, **kwargs):

    if principal is None:
        principal = {}
    if context is None:
        context = {}

    # Use real engine if available
    if _real and hasattr(_real, "infer_risk"):
        return _real.infer_risk(action, principal, context)

    # Fallback
    return _fallback_risk(action, principal, context)


def generate_synthetic_data(n: int = 5) -> List[Dict[str, Any]]:

    out = []

    for i in range(int(n)):
        out.append(
            {
                "id": f"syn_{i}",
                "amount": 1000 + i * 100,
                "country": "IN",
                "ts": i,
            }
        )

    return out
