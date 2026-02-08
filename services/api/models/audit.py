from pydantic import BaseModel
from datetime import datetime

class AuditEventResponse(BaseModel):
    id: str
    action: str
    actor: str
    created_at: datetime
