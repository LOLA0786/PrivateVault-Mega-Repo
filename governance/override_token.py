from dataclasses import dataclass
from datetime import datetime

@dataclass
class OverrideToken:
    decision_type: str
    approvers: list
    justification: str
    mode: str  # standard | break_glass | quorum
    issued_at: datetime
    expires_at: datetime
