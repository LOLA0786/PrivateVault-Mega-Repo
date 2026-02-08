from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class QuorumRulesResponse(BaseModel):
    rules: Dict[str, Any]


class QuorumRulesUpdateRequest(BaseModel):
    rules: Dict[str, Any]


class QuorumValidateRequest(BaseModel):
    action: str
    payload: Dict[str, Any]
    approvals: List[str]
    tenant_id: Optional[str] = None


class QuorumValidateResponse(BaseModel):
    valid: bool
    required: int
    approved: int
    missing: Optional[int] = None
