from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TenantCreateRequest(BaseModel):
    tenant_id: str = Field(..., min_length=3)
    name: str
    metadata: Optional[dict] = None


class TenantUpdateRequest(BaseModel):
    name: Optional[str] = None
    metadata: Optional[dict] = None


class TenantResponse(BaseModel):
    tenant_id: str
    name: str
    metadata: Optional[dict] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
