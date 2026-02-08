from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EvidenceExportRequest(BaseModel):
    tenant_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    format: str = "json"


class EvidenceExportResponse(BaseModel):
    export_id: str
    status: str
    download_url: Optional[str] = None
    created_at: str = datetime.utcnow().isoformat()
