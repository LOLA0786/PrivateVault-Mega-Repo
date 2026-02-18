from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DecisionAuthority:
    decision_type: str
    owner_role: str
    delegates: List[str] = field(default_factory=list)
    escalation_role: Optional[str] = None
    quorum_required: bool = False
    quorum_roles: List[str] = field(default_factory=list)
    jurisdiction: List[str] = field(default_factory=list)
    risk_threshold: int = 0
