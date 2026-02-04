import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, Request

from intent_binding import canonical_hash
from security_context import _load_context_keys


DEFAULT_QUORUM_MIN = 2
DEFAULT_RULE_ID = "legacy"


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


def _parse_yaml(raw: str) -> Any:
    try:
        import yaml  # type: ignore
    except Exception:
        raise HTTPException(status_code=500, detail="QUORUM_YAML_UNAVAILABLE")
    try:
        return yaml.safe_load(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="QUORUM_YAML_INVALID")


def _load_v2_rules() -> Dict[str, Any]:
    rules_file = os.getenv("PV_QUORUM_RULES_FILE")
    if rules_file:
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                raw = f.read()
        except Exception:
            raise HTTPException(status_code=500, detail="QUORUM_RULES_FILE_INVALID")
        if rules_file.endswith((".yml", ".yaml")):
            rules = _parse_yaml(raw)
        else:
            try:
                rules = json.loads(raw)
            except Exception:
                raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
        if not isinstance(rules, dict):
            raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
        return rules

    rules_yaml = os.getenv("PV_QUORUM_RULES_YAML")
    if rules_yaml:
        rules = _parse_yaml(rules_yaml)
        if not isinstance(rules, dict):
            raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
        return rules

    rules_json = os.getenv("PV_QUORUM_RULES_V2")
    if rules_json:
        try:
            rules = json.loads(rules_json)
        except Exception:
            raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
        if not isinstance(rules, dict):
            raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
        return rules

    return {}


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


def _get_revoked_approval_ids() -> List[str]:
    raw = os.getenv("PV_QUORUM_REVOKED_IDS")
    if not raw:
        return []
    try:
        revoked = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="QUORUM_REVOKED_IDS_INVALID")
    if not isinstance(revoked, list):
        raise HTTPException(status_code=500, detail="QUORUM_REVOKED_IDS_INVALID")
    return [str(a) for a in revoked]


def _verify_approval_signature(secret: str, intent_hash: str, signature: str) -> None:
    expected = hmac.new(secret.encode("utf-8"), intent_hash.encode("utf-8"), hashlib.sha256)
    if not hmac.compare_digest(expected.hexdigest(), signature):
        raise HTTPException(status_code=403, detail="APPROVAL_SIGNATURE_INVALID")


def _merge_rule(base: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not override:
        return dict(base)
    merged = dict(base)
    for key, value in override.items():
        merged[key] = value
    return merged


def _resolve_v2_rule(tenant_id: Optional[str], action: str) -> Dict[str, Any]:
    rules = _load_v2_rules()
    if not rules:
        return {}

    global_defaults = rules.get("defaults", {}) if isinstance(rules.get("defaults"), dict) else {}
    global_actions = rules.get("actions", {}) if isinstance(rules.get("actions"), dict) else {}
    tenant_block = {}
    if tenant_id and isinstance(rules.get("tenants"), dict):
        tenant_block = rules["tenants"].get(tenant_id, {})
    tenant_defaults = (
        tenant_block.get("defaults", {}) if isinstance(tenant_block.get("defaults"), dict) else {}
    )
    tenant_actions = (
        tenant_block.get("actions", {}) if isinstance(tenant_block.get("actions"), dict) else {}
    )

    rule = _merge_rule(global_defaults, global_actions.get(action))
    rule = _merge_rule(rule, tenant_defaults)
    rule = _merge_rule(rule, tenant_actions.get(action))
    if not rule:
        return {}

    rule["rule_id"] = rule.get("rule_id") or f"tenant:{tenant_id or '*'}|action:{action}"
    return rule


def _get_rule_min_approvals(rule: Dict[str, Any], action: str) -> int:
    if rule and rule.get("min_approvals") is not None:
        try:
            return int(rule["min_approvals"])
        except Exception:
            raise HTTPException(status_code=500, detail="QUORUM_MIN_INVALID")
    return _get_quorum_min(action)


def _normalize_list(value: Any) -> Optional[List[str]]:
    if value is None:
        return None
    if not isinstance(value, list):
        raise HTTPException(status_code=500, detail="QUORUM_RULES_INVALID")
    return [str(v) for v in value]


def _approval_is_expired(approval: Dict[str, Any]) -> bool:
    expires_at = approval.get("expires_at")
    if expires_at is None:
        return False
    try:
        return int(time.time()) > int(expires_at)
    except Exception:
        return True


def _approval_is_too_old(approval: Dict[str, Any], max_age: Optional[int]) -> bool:
    if not max_age:
        return False
    issued_at = approval.get("issued_at")
    if issued_at is None:
        return True
    try:
        issued = int(issued_at)
    except Exception:
        return True
    return (int(time.time()) - issued) > int(max_age)


async def require_quorum_for_emit(request: Request) -> Dict[str, Any]:
    action = f"{request.method.upper()} {request.url.path}"
    context = getattr(request.state, "pv_context", {}) or {}
    tenant_id = context.get("tenant_id")
    rule = _resolve_v2_rule(tenant_id, action)
    min_required = _get_rule_min_approvals(rule, action)

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
    revoked_ids = set(_get_revoked_approval_ids())
    rule_allowlist = _normalize_list(rule.get("allow_approver_ids")) if rule else None
    roles_required = _normalize_list(rule.get("roles_required")) if rule else None
    roles_optional = _normalize_list(rule.get("roles_optional")) if rule else None
    approver_regions = _normalize_list(rule.get("approver_regions")) if rule else None
    require_distinct_roles = bool(rule.get("require_distinct_roles")) if rule else False
    require_approval_id = bool(rule.get("require_approval_id")) if rule else False
    max_age = rule.get("max_approvals_age_seconds") if rule else None

    approvers_seen = set()
    roles_seen = set()
    valid_approvals = []

    for approval in approvals:
        if not isinstance(approval, dict):
            continue
        approver_id = approval.get("approver_id")
        key_id = approval.get("key_id")
        signature = approval.get("signature")
        approval_intent_hash = approval.get("intent_hash")
        approval_id = approval.get("approval_id")
        role = approval.get("role")
        region = approval.get("region")
        if not approver_id or not key_id or not signature:
            continue
        if approval_intent_hash != intent_hash:
            continue
        if require_approval_id and not approval_id:
            continue
        if approval.get("revoked"):
            continue
        if approval_id and approval_id in revoked_ids:
            continue
        if _approval_is_expired(approval):
            continue
        if _approval_is_too_old(approval, max_age):
            continue
        if approver_regions and region not in approver_regions:
            continue
        if roles_required or roles_optional:
            allowed_roles = set(roles_required or []) | set(roles_optional or [])
            if not role or role not in allowed_roles:
                continue
        if allowlist and approver_id not in allowlist:
            continue
        if rule_allowlist and approver_id not in rule_allowlist:
            continue
        secret = context_keys.get(str(key_id))
        if not secret:
            continue
        _verify_approval_signature(secret, intent_hash, signature)
        if approver_id in approvers_seen:
            continue
        approvers_seen.add(approver_id)
        valid_approvals.append(approval)
        if role:
            roles_seen.add(str(role))

    if roles_required:
        for role in roles_required:
            if role not in roles_seen:
                raise HTTPException(status_code=403, detail="QUORUM_ROLE_MISSING")
        min_required = max(min_required, len(roles_required))

    if require_distinct_roles:
        approved_count = len(roles_seen)
    else:
        approved_count = len(valid_approvals)

    if approved_count < min_required:
        raise HTTPException(status_code=403, detail="QUORUM_NOT_MET")

    quorum_info = {
        "required": min_required,
        "approved": approved_count,
        "approvers": sorted(approvers_seen),
        "roles": sorted(roles_seen),
        "intent_hash": intent_hash,
        "tenant_id": tenant_id,
        "action": action,
        "rule_id": rule.get("rule_id") if rule else DEFAULT_RULE_ID,
        "approvals_used": [
            {
                "approval_id": a.get("approval_id"),
                "approver_id": a.get("approver_id"),
                "role": a.get("role"),
                "region": a.get("region"),
                "intent_hash": a.get("intent_hash"),
                "issued_at": a.get("issued_at"),
                "expires_at": a.get("expires_at"),
            }
            for a in valid_approvals
        ],
    }
    request.state.pv_quorum = quorum_info
    return quorum_info
