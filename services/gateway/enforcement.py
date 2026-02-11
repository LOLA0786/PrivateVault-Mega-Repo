from datetime import datetime
from typing import Any, Dict

from services.api.governance.policy_engine import evaluate_policy


def enforce(
    action: str,
    tenant_id: str,
    payload: str | None = "",
    context: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Unified enforcement engine.

    - Evaluates payload against tenant policy
    - Handles shadow / monitor vs strict modes
    - Returns enterprise-grade structured response
    """

    context = context or {}
    payload = payload or ""

    decision = evaluate_policy(
        message=payload,
        tenant_id=tenant_id,
    )

    mode = decision.get("mode", "monitor")
    would_block = decision.get("decision") == "BLOCK"

    # Shadow / Monitor Mode
    if mode in ("monitor", "shadow"):
        enforced = False
        allowed = True
    else:
        enforced = would_block
        allowed = not would_block

    result = {
        "action": action,
        "tenant_id": tenant_id,
        "allowed": allowed,
        "enforced": enforced,
        "shadow": mode in ("monitor", "shadow"),
        "would_have_blocked": would_block,
        "decision": decision,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    return result
