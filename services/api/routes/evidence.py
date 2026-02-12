from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/evidence", tags=["evidence"])


class EvidenceExportRequest(BaseModel):
    tenant_id: str
    start: str
    end: str
    bundle_name: str


class EvidenceItem(BaseModel):
    id: str
    type: str
    hash: str
    timestamp: str


class EvidenceExportResponse(BaseModel):
    bundle_id: str
    tenant_id: str
    count: int
    evidence: List[EvidenceItem]


@router.post("/export", response_model=EvidenceExportResponse)
async def export_evidence(req: EvidenceExportRequest, request: Request):
    return {
        "bundle_id": req.bundle_name,
        "tenant_id": req.tenant_id,
        "count": 1,
        "evidence": [
            {
                "id": "evt_001",
                "type": "POLICY_DECISION",
                "hash": "0xabc",
                "timestamp": "2026-02-08T12:01:00Z",
            }
        ],
    }


@router.get("/health")
async def health():
    return {"ok": True}
