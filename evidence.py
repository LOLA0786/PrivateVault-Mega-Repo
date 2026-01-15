"""
Evidence generation + verification.

Contract used by regression tests:
- generate_evidence(intent, decision, policy_version) returns:
    {
      "policy_version": str,
      "decision": bool,
      "reason": str|None,
      "evidence_hash": str,
      "timestamp": iso8601 string
    }
- verify_evidence(intent, decision, policy_version, evidence_hash) returns bool
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
import hashlib
import json


def _canonicalize_decision(decision: Any) -> Dict[str, Any]:
    """
    Tests sometimes pass full dict decision objects, sometimes bool.
    We canonicalize to stable dict -> then hash deterministically.

    IMPORTANT: evidence_hash must be independent of volatile fields like timestamp.
    """
    if isinstance(decision, dict):
        allowed = bool(decision.get("allowed", False))
        reason = decision.get("reason")
        pv = decision.get("policy_version")
    else:
        allowed = bool(decision)
        reason = None
        pv = None

    return {
        "allowed": allowed,
        "reason": reason,
        "policy_version": pv,
    }


def _pv_hash(intent: Dict[str, Any], decision: Any, policy_version: str) -> str:
    """
    Single deterministic hash function for both generate + verify.
    """
    payload = {
        "intent": intent,
        "decision": _canonicalize_decision(decision),
        "policy_version": policy_version,
    }
    b = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def generate_evidence(intent: Dict[str, Any], decision: Any, policy_version: Optional[str] = None) -> Dict[str, Any]:
    policy_version = policy_version or (decision.get("policy_version") if isinstance(decision, dict) else "unknown") or "unknown"
    canon = _canonicalize_decision(decision)

    evidence_hash = _pv_hash(intent, decision, policy_version)

    return {
        "policy_version": policy_version,
        "decision": bool(canon["allowed"]),
        "reason": canon.get("reason"),
        "evidence_hash": evidence_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def verify_evidence(intent: Dict[str, Any], decision: Any, policy_version: str, evidence_hash: str) -> bool:
    try:
        expected = _pv_hash(intent, decision, policy_version)
        return expected == evidence_hash
    except Exception:
        return False
