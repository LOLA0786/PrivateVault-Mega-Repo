from fastapi import APIRouter, Depends, HTTPException

from evidence_export import export_bundle
from services.api.middleware.auth import AuthContext, require_auth, require_scope
from services.api.models import EvidenceExportRequest, EvidenceExportResponse

router = APIRouter()


@router.post("/evidence/export", response_model=EvidenceExportResponse)
def evidence_export(payload: EvidenceExportRequest, auth: AuthContext = Depends(require_auth)):
    require_scope(auth, "evidence:export")
    tenant_id = payload.tenant_id or auth.tenant_id
    if not tenant_id:
        raise HTTPException(status_code=400, detail="TENANT_REQUIRED")
    if auth.tenant_id and tenant_id != auth.tenant_id:
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_VIOLATION")
    try:
        result = export_bundle(
            tenant_id=tenant_id,
            start_iso=payload.start,
            end_iso=payload.end,
            bundle_name=payload.bundle_name,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {
        "bundle_id": result.bundle_id,
        "bundle_path": result.bundle_path,
        "manifest_hash": result.manifest_hash,
        "verified": result.verified,
        "warnings": result.warnings,
    }
