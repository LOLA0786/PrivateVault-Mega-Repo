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
