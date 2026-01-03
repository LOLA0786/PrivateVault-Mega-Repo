from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class DecisionContext:
    intent_hash: str
    policy_version: str
    regulatory_snapshot: str
    entropy_seed: int
    timestamp: str = datetime.now(timezone.utc).isoformat()
