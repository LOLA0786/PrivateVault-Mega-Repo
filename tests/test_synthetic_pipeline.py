#!/usr/bin/env python3
"""
Synthetic pipeline test.

NOTE:
This file is executed under pytest, so sys.argv contains pytest flags
(e.g. -q, -k, -vv). We must NOT assume sys.argv[1] is an integer.
"""

import sys

from policy_engine import generate_synthetic_data, authorize_intent, infer_risk


def _parse_n_from_argv(default: int = 5) -> int:
    if len(sys.argv) <= 1:
        return default
    try:
        return int(sys.argv[1])
    except Exception:
        return default


# Script-style execution (import-time)
n = _parse_n_from_argv(default=5)

principal = {"id": "agent_synth", "role": "agent", "type": "agent", "trust_level": "high"}
context = {"amount": 12345}

data = generate_synthetic_data(n=n)
decision = authorize_intent("generate_synthetic_data", principal, context)
risk = infer_risk("generate_synthetic_data", principal, context)

print("Synthetic records:", len(data))
print("Decision:", decision)
print("Risk:", risk)

# pytest-friendly assertion so it counts as a real test
def test_synthetic_pipeline_executes():
    assert isinstance(data, list)
    assert len(data) == n
    assert "allowed" in decision or "ok" in decision
    assert isinstance(risk, dict)
