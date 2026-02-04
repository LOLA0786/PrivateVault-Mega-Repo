from typing import List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str = "ok"


class StatusResponse(BaseModel):
    status: str
    version: str


class AuthToken(BaseModel):
    token: str
    scopes: List[str]
    tenant_id: Optional[str] = None


class TenantCreateRequest(BaseModel):
    tenant_id: str
    name: str
    region: Optional[str] = None


class TenantUpdateRequest(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None


class TenantResponse(BaseModel):
    tenant_id: str
    name: str
    region: Optional[str] = None


class QuorumValidateRequest(BaseModel):
    action: str
    payload: dict
    approvals: list
    tenant_id: Optional[str] = None


class QuorumValidateResponse(BaseModel):
    required: int
    approved: int
    approvers: list
    roles: list
    intent_hash: str
    tenant_id: Optional[str] = None
    action: str
    rule_id: str


class QuorumRulesResponse(BaseModel):
    rules: dict


class QuorumRulesUpdateRequest(BaseModel):
    rules: dict


class AuditEventResponse(BaseModel):
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


class ApprovalRecord(BaseModel):
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


class EvidenceExportRequest(BaseModel):
    tenant_id: Optional[str] = None
    start: str
    end: str
    bundle_name: Optional[str] = None


class EvidenceExportResponse(BaseModel):
    bundle_id: str
    bundle_path: str
    manifest_hash: str
    verified: bool
    warnings: list
