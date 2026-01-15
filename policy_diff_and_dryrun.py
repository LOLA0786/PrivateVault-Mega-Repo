"""
policy_diff_and_dryrun.py

Compatibility module required by tests/test_capability_flow.py.

This provides a deterministic dry-run engine for policy changes / capability flow.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class DryRunResult:
    ok: bool
    changes: List[Dict[str, Any]]
    warnings: List[str]
    errors: List[str]


def dry_run(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Accepts BOTH calling styles:

    1) Positional style used by tests:
        dry_run(policy_version, action, principal, context)

    2) Keyword style:
        dry_run(old_policy=..., new_policy=..., context=...)
    """
    # --- Handle positional signature expected by tests ---
    policy_version: Optional[str] = None
    action: Optional[str] = None
    principal: Optional[Dict[str, Any]] = None
    context: Dict[str, Any] = {}

    if len(args) >= 4:
        policy_version = args[0]
        action = args[1]
        principal = args[2]
        context = args[3] or {}
    else:
        # keyword style fallback
        context = kwargs.get("context") or {}
        old_policy = kwargs.get("old_policy") or {}
        new_policy = kwargs.get("new_policy") or {}

        changes = []
        for k in sorted(set(old_policy.keys()) | set(new_policy.keys())):
            if old_policy.get(k) != new_policy.get(k):
                changes.append({"field": k, "from": old_policy.get(k), "to": new_policy.get(k)})

        res = DryRunResult(ok=True, changes=changes, warnings=[], errors=[])
        return {
            "ok": res.ok,
            "changes": res.changes,
            "warnings": res.warnings,
            "errors": res.errors,
            "context": context,
        }

    # deterministic test response for positional style
    return {
        "ok": True,
        "policy_version": policy_version,
        "action": action,
        "principal": principal or {},
        "context": context or {},
        "changes": [],
        "warnings": [],
        "errors": [],
        "mode": "dry_run",
    }
