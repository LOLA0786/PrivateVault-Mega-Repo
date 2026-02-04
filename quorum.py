import hashlib
import hmac
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, Request

from intent_binding import canonical_hash
from security_context import _load_context_keys


DEFAULT_QUORUM_MIN = 2


def _parse_json_header(raw: Optional[str], error_detail: str) -> Any:
    if not raw:
        raise HTTPException(status_code=403, detail=error_detail)
    try:
        return json.loads(raw)
    except Exception:
        raise HTTPException(status_code=400, detail=error_detail)


def _get_quorum_rules() -> Dict[str, Any]:
    raw = os.getenv("PV_QUORUM_RULES")
    if not raw:
        return {}
    try:
        rules = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
    if not isinstance(rules, dict):
        raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
    return rules


def _get_quorum_min(action: str) -> int:
    rules = _get_quorum_rules()
    value = rules.get(action)
    if value is None:
        value = os.getenv("PV_QUORUM_MIN", str(DEFAULT_QUORUM_MIN))
    try:
        return int(value)
    except Exception:
        raise HTTPException(status_code=500, detail="QUORUM_MIN_INVALID")


def _get_approver_allowlist() -> Optional[List[str]]:
    raw = os.getenv("PV_QUORUM_APPROVER_ALLOWLIST")
    if not raw:
        return None
    try:
        allowlist = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="QUORUM_ALLOWLIST_INVALID")
    if not isinstance(allowlist, list):
        raise HTTPException(status_code=500, detail="QUORUM_ALLOWLIST_INVALID")
    return [str(a) for a in allowlist]


def _verify_approval_signature(secret: str, intent_hash: str, signature: str) -> None:
    expected = hmac.new(secret.encode("utf-8"), intent_hash.encode("utf-8"), hashlib.sha256)
    if not hmac.compare_digest(expected.hexdigest(), signature):
        raise HTTPException(status_code=403, detail="APPROVAL_SIGNATURE_INVALID")


async def require_quorum_for_emit(request: Request) -> Dict[str, Any]:
    action = f"{request.method.upper()} {request.url.path}"
    min_required = _get_quorum_min(action)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="PAYLOAD_INVALID")

    intent_hash = canonical_hash(payload)

    approvals_raw = request.headers.get("X-PV-Approvals")
    approvals = _parse_json_header(approvals_raw, "QUORUM_REQUIRED")
    if not isinstance(approvals, list):
        raise HTTPException(status_code=400, detail="APPROVALS_INVALID")

    context_keys = _load_context_keys()
    allowlist = _get_approver_allowlist()
    approvers_seen = set()
    valid_approvals = []

    for approval in approvals:
        if not isinstance(approval, dict):
            continue
        approver_id = approval.get("approver_id")
        key_id = approval.get("key_id")
        signature = approval.get("signature")
        approval_intent_hash = approval.get("intent_hash")
        if not approver_id or not key_id or not signature:
            continue
        if approval_intent_hash != intent_hash:
            continue
        if allowlist and approver_id not in allowlist:
            continue
        secret = context_keys.get(str(key_id))
        if not secret:
            continue
        _verify_approval_signature(secret, intent_hash, signature)
        if approver_id in approvers_seen:
            continue
        approvers_seen.add(approver_id)
        valid_approvals.append(approval)

    if len(valid_approvals) < min_required:
        raise HTTPException(status_code=403, detail="QUORUM_NOT_MET")

    quorum_info = {
        "required": min_required,
        "approved": len(valid_approvals),
        "approvers": sorted(approvers_seen),
        "intent_hash": intent_hash,
    }
    request.state.pv_quorum = quorum_info
    return quorum_info
