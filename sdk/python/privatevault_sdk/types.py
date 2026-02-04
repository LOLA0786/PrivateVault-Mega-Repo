from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class StatusResponse:
    status: str
    version: str


@dataclass
class HealthResponse:
    status: str


@dataclass
class AuthToken:
    token: str
    scopes: List[str]
    tenant_id: Optional[str] = None


@dataclass
class Tenant:
    tenant_id: str
    name: str
    region: Optional[str] = None


@dataclass
class QuorumRules:
    rules: Dict[str, Any]


@dataclass
class QuorumValidateResponse:
    required: int
    approved: int
    approvers: List[str]
    roles: List[str]
    intent_hash: str
    tenant_id: Optional[str]
    action: str
    rule_id: str


@dataclass
class EvidenceExportResponse:
    bundle_id: str
    bundle_path: str
    manifest_hash: str
    verified: bool
    warnings: List[str]


@dataclass
class AuditEvent:
    timestamp: str
    event_type: str
    method: str
    path: str
    status_code: int
    decision: str
    latency_ms: int
    actor_id: Optional[str] = None
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    request_hash: Optional[str] = None
    quorum: Optional[dict] = None
    error: Optional[str] = None
    client_ip: Optional[str] = None


@dataclass
class ApprovalRecord:
    approval_id: Optional[str] = None
    approver_id: Optional[str] = None
    role: Optional[str] = None
    region: Optional[str] = None
    intent_hash: Optional[str] = None
    issued_at: Optional[int] = None
    expires_at: Optional[int] = None
    rule_id: Optional[str] = None
    tenant_id: Optional[str] = None
    action: Optional[str] = None
    timestamp: Optional[str] = None
