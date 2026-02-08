from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ApprovalRecord(BaseModel):
    approval_id: str
    action: str
    status: str
    approver: Optional[str] = None
    created_at: str = datetime.utcnow().isoformat()
