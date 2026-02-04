import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from audit_logger import get_audit_log_paths


DENY_PATTERNS = [
    re.compile(r"(secret|token|password|credential|authorization|api_key)", re.IGNORECASE)
]

AUDIT_ALLOWLIST = {
    "timestamp",
    "event_type",
    "method",
    "path",
    "status_code",
    "decision",
    "latency_ms",
    "actor_id",
    "tenant_id",
    "role",
    "request_hash",
    "quorum",
    "error",
    "client_ip",
}

APPROVAL_ALLOWLIST = {
    "approval_id",
    "approver_id",
    "role",
    "region",
    "intent_hash",
    "issued_at",
    "expires_at",
    "rule_id",
    "tenant_id",
    "action",
    "timestamp",
}

CONTEXT_ALLOWLIST = {
    "timestamp",
    "actor_id",
    "tenant_id",
    "role",
    "request_hash",
    "method",
    "path",
}

POLICY_ALLOWLIST = {"version", "created_at", "active"}


@dataclass
class ExportResult:
    bundle_id: str
    bundle_path: str
    manifest_hash: str
    verified: bool
    warnings: List[str]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def _is_ts_in_range(ts: str, start: datetime, end: datetime) -> bool:
    try:
        parsed = _parse_iso(ts)
    except Exception:
        return False
    return start <= parsed <= end


def _ensure_export_root() -> str:
    export_root = os.getenv("PV_EXPORT_ROOT")
    if not export_root:
        raise RuntimeError("PV_EXPORT_ROOT_REQUIRED")
    export_root = os.path.realpath(export_root)
    os.makedirs(export_root, exist_ok=True)
    return export_root


def _safe_bundle_path(export_root: str, bundle_name: str) -> str:
    candidate = os.path.realpath(os.path.join(export_root, bundle_name))
    if not (candidate == export_root or candidate.startswith(export_root + os.sep)):
        raise RuntimeError("EXPORT_PATH_OUTSIDE_ROOT")
    return candidate


def _hash_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_jsonl(path: str, rows: Iterable[Dict[str, Any]]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        cleaned = {}
        for key, val in value.items():
            if any(pattern.search(str(key)) for pattern in DENY_PATTERNS):
                continue
            cleaned[key] = _redact(val)
        return cleaned
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _allowlist(value: Dict[str, Any], allowlist: set) -> Dict[str, Any]:
    filtered = {k: value.get(k) for k in allowlist if k in value}
    return _redact(filtered)


def _load_audit_events(tenant_id: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    for path in get_audit_log_paths():
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except Exception:
                    continue
                if event.get("tenant_id") != tenant_id:
                    continue
                ts = event.get("timestamp")
                if not ts or not _is_ts_in_range(ts, start, end):
                    continue
                events.append(_allowlist(event, AUDIT_ALLOWLIST))
    events.sort(key=lambda e: e.get("timestamp", ""))
    return events


def _extract_approvals(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    approvals: List[Dict[str, Any]] = []
    for event in events:
        quorum = event.get("quorum") or {}
        approvals_used = quorum.get("approvals_used") or []
        for approval in approvals_used:
            row = dict(approval)
            row["rule_id"] = quorum.get("rule_id")
            row["tenant_id"] = event.get("tenant_id")
            row["action"] = quorum.get("action")
            row["timestamp"] = event.get("timestamp")
            approvals.append(_allowlist(row, APPROVAL_ALLOWLIST))
    approvals.sort(key=lambda a: (a.get("timestamp", ""), a.get("approval_id", "")))
    return approvals


def _extract_context_signatures(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    signatures = []
    for event in events:
        row = {
            "timestamp": event.get("timestamp"),
            "actor_id": event.get("actor_id"),
            "tenant_id": event.get("tenant_id"),
            "role": event.get("role"),
            "request_hash": event.get("request_hash"),
            "method": event.get("method"),
            "path": event.get("path"),
        }
        signatures.append(_allowlist(row, CONTEXT_ALLOWLIST))
    signatures.sort(key=lambda s: s.get("timestamp", ""))
    return signatures


def _load_policy_versions() -> List[Dict[str, Any]]:
    try:
        import policy_registry
    except Exception:
        return []

    if not hasattr(policy_registry, "load_policies"):
        return []

    try:
        policies = policy_registry.load_policies()
    except Exception:
        return []

    if not isinstance(policies, dict):
        return []

    versions = []
    for version, data in policies.items():
        if not isinstance(data, dict):
            continue
        record = {"version": version, "created_at": data.get("created_at"), "active": data.get("active")}
        versions.append(_allowlist(record, POLICY_ALLOWLIST))
    versions.sort(key=lambda v: v.get("created_at") or "")
    return versions


def _load_decision_ledger(tenant_id: str, start: datetime, end: datetime) -> Tuple[List[Dict[str, Any]], Dict[str, Any], List[str]]:
    warnings: List[str] = []
    ledger_path = os.getenv("PV_DECISION_LEDGER_PATH", "ai_firewall_ledger.jsonl")
    if not os.path.exists(ledger_path):
        warnings.append("DECISION_LEDGER_MISSING")
        return [], {"verified": False, "reason": "MISSING"}, warnings

    verified = True
    chain_info: Dict[str, Any] = {"verified": True, "reason": "OK"}
    entries: List[Dict[str, Any]] = []

    try:
        from decision_ledger import DecisionLedger, GENESIS_HASH

        ledger = DecisionLedger(log_file=ledger_path, auto_load=True)
        chain = ledger.chain
        if chain:
            chain_info.update(
                {
                    "count": len(chain),
                    "first_hash": chain[0].get("hash"),
                    "last_hash": chain[-1].get("hash"),
                    "genesis_hash": GENESIS_HASH,
                }
            )
    except Exception:
        verified = False
        chain_info["verified"] = False
        chain_info["reason"] = "UNVERIFIED"

    # Always try to load entries, even if verification fails
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            ts = entry.get("timestamp")
            if not ts or not _is_ts_in_range(ts, start, end):
                continue
            data = entry.get("data") or {}
            if tenant_id and data.get("tenant_id") != tenant_id:
                continue
            entries.append(_redact(entry))

    entries.sort(key=lambda e: e.get("timestamp", ""))
    if not verified:
        warnings.append("DECISION_LEDGER_UNVERIFIED")
    return entries, chain_info, warnings


def export_bundle(
    *,
    tenant_id: str,
    start_iso: str,
    end_iso: str,
    bundle_name: Optional[str] = None,
) -> ExportResult:
    export_root = _ensure_export_root()
    start = _parse_iso(start_iso)
    end = _parse_iso(end_iso)
    if end < start:
        raise RuntimeError("EXPORT_RANGE_INVALID")

    bundle_id = bundle_name or f"EVB-{tenant_id}-{start.strftime('%Y%m%d%H%M%S')}-{end.strftime('%Y%m%d%H%M%S')}"
    bundle_path = _safe_bundle_path(export_root, bundle_id)
    if os.path.exists(bundle_path):
        shutil.rmtree(bundle_path)
    os.makedirs(bundle_path, exist_ok=True)

    warnings: List[str] = []

    audit_events = _load_audit_events(tenant_id, start, end)
    approvals = _extract_approvals(audit_events)
    contexts = _extract_context_signatures(audit_events)
    policy_versions = _load_policy_versions()
    decision_records, chain_info, ledger_warnings = _load_decision_ledger(tenant_id, start, end)
    warnings.extend(ledger_warnings)

    audit_path = os.path.join(bundle_path, "audit_logs.jsonl")
    approvals_path = os.path.join(bundle_path, "approvals.jsonl")
    contexts_path = os.path.join(bundle_path, "context_signatures.jsonl")
    policy_path = os.path.join(bundle_path, "policy_versions.json")
    decision_path = os.path.join(bundle_path, "decision_records.jsonl")
    hash_chain_path = os.path.join(bundle_path, "hash_chain.json")

    _write_jsonl(audit_path, audit_events)
    _write_jsonl(approvals_path, approvals)
    _write_jsonl(contexts_path, contexts)
    _write_json(policy_path, policy_versions)
    _write_jsonl(decision_path, decision_records)
    _write_json(hash_chain_path, chain_info)

    evidence_summary = {
        "tenant_id": tenant_id,
        "range": {"start": start_iso, "end": end_iso},
        "counts": {
            "audit_events": len(audit_events),
            "approvals": len(approvals),
            "policy_versions": len(policy_versions),
            "decision_records": len(decision_records),
            "context_signatures": len(contexts),
        },
        "decision_ledger_verified": bool(chain_info.get("verified")),
        "warnings": warnings,
    }
    evidence_json_path = os.path.join(bundle_path, "evidence.json")
    _write_json(evidence_json_path, evidence_summary)

    evidence_md_path = os.path.join(bundle_path, "evidence.md")
    with open(evidence_md_path, "w", encoding="utf-8") as f:
        f.write("# PrivateVault Compliance Evidence Bundle\n\n")
        f.write(f"- Tenant: `{tenant_id}`\n")
        f.write(f"- Range: `{start_iso}` to `{end_iso}`\n")
        f.write(f"- Audit events: `{len(audit_events)}`\n")
        f.write(f"- Approvals: `{len(approvals)}`\n")
        f.write(f"- Policy versions: `{len(policy_versions)}`\n")
        f.write(f"- Decision records: `{len(decision_records)}`\n")
        f.write(f"- Context signatures: `{len(contexts)}`\n")
        f.write(f"- Decision ledger verified: `{bool(chain_info.get('verified'))}`\n")
        if warnings:
            f.write("- Warnings:\n")
            for warning in warnings:
                f.write(f"  - {warning}\n")

    manifest = {
        "bundle_id": bundle_id,
        "generated_at": _utc_now_iso(),
        "tenant_id": tenant_id,
        "range": {"start": start_iso, "end": end_iso},
        "schema_version": "1.0",
        "sources": {
            "audit_paths": get_audit_log_paths(),
            "policy_source": "policy_registry.load_policies",
            "decision_ledger_path": os.getenv("PV_DECISION_LEDGER_PATH", "ai_firewall_ledger.jsonl"),
        },
        "warnings": warnings,
    }
    manifest_path = os.path.join(bundle_path, "manifest.json")
    _write_json(manifest_path, manifest)

    hashes_dir = os.path.join(bundle_path, "hashes")
    os.makedirs(hashes_dir, exist_ok=True)
    hash_manifest_path = os.path.join(hashes_dir, "sha256sum.txt")

    files_to_hash = [
        audit_path,
        approvals_path,
        contexts_path,
        policy_path,
        decision_path,
        hash_chain_path,
        evidence_json_path,
        evidence_md_path,
        manifest_path,
    ]
    hash_lines = []
    for file_path in sorted(files_to_hash):
        hash_lines.append(f"{_hash_file(file_path)}  {os.path.relpath(file_path, bundle_path)}")
    with open(hash_manifest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(hash_lines) + "\n")

    manifest_hash = _hash_file(hash_manifest_path)
    return ExportResult(
        bundle_id=bundle_id,
        bundle_path=bundle_path,
        manifest_hash=manifest_hash,
        verified=bool(chain_info.get("verified")),
        warnings=warnings,
    )
