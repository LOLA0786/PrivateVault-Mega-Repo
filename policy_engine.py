"""
Standalone-compatible policy engine wrapper.

Uses galani engine if present.
Falls back to internal logic if not.
"""

from typing import Any, Dict, List
import importlib


def _load_real():
    try:
        return importlib.import_module("galani.core.policy_engine")
    except ImportError:
        return None


_real = _load_real()


def _extract_action_name(action):
    if isinstance(action, str):
        return action
    if isinstance(action, dict):
        return action.get("tool") or action.get("action")
    return None


def _fallback_authorize(action, principal, context):

    action_name = _extract_action_name(action)

    trust = (principal or {}).get("trust_level", "unknown")

    # Allow amount from context OR action
    amount = 0
    if isinstance(action, dict):
        amount = float(action.get("amount", 0) or 0)
    if context:
        amount = float(context.get("amount", amount) or 0)

    # --- HARD LIMIT POLICY ---
    if action_name == "transfer_funds" and amount > 10000:
        return {
            "allowed": False,
            "policy": "fallback_v2_hard_limit",
            "reason": "Amount exceeds deterministic hard limit"
        }

    # --- TRUST-BASED POLICY ---
    if trust == "low" and amount > 300000:
        return {
            "allowed": False,
            "policy": "fallback_v2_trust",
            "reason": "Low trust principal over threshold"
        }

    return {
        "allowed": True,
        "policy": "fallback_v2",
        "reason": "local_policy_engine",
    }


def _fallback_risk(action, principal, context):

    amt = 0
    if isinstance(action, dict):
        amt = float(action.get("amount", 0) or 0)
    if context:
        amt = float(context.get("amount", amt) or 0)

    score = min(1.0, amt / 500000.0)

    return {
        "risk_score": score,
        "risk_level": "high" if score > 0.7 else "medium" if score > 0.4 else "low",
        "model": "fallback_static",
    }


def authorize_intent(action, principal=None, context=None, **kwargs):

    if principal is None:
        principal = {}
    if context is None:
        context = {}

    if _real and hasattr(_real, "authorize_intent"):

        enveloped = {
            "action": action,
            "principal": principal,
            "context": context,
            "policy_version": kwargs.get("policy_version", "v1"),
        }

        return _real.authorize_intent(enveloped, **kwargs)

    return _fallback_authorize(action, principal, context)


def infer_risk(action, principal=None, context=None, **kwargs):

    if principal is None:
        principal = {}
    if context is None:
        context = {}

    if _real and hasattr(_real, "infer_risk"):
        return _real.infer_risk(action, principal, context)

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
