"""
Compatibility shim for legacy tests.

Real implementation lives under src/ layout:
  src/galani/governance/policy_registry.py

When PYTHONPATH includes ./src, imports must be:
  galani.governance.policy_registry
"""
try:
    from galani.governance.policy_registry import *  # noqa
except Exception as e:
    _IMPORT_ERROR = e
