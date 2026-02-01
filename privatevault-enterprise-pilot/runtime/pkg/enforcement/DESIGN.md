# Enforcement Plane — DESIGN

## Contract
Inputs:
- request: method, path, headers, body hash
- user: id, roles (optional header injected by governance)
- agent: id
- env/system identifiers
Outputs:
- allow/deny boolean
- reason code
- policy version hash

## Invariants
- Default deny if policy missing.
- Low latency: <5ms budget.
- No stateful dependencies.

## Failure Modes
- WASM not loaded -> deny all
- malformed input -> deny
- unknown action -> deny

## Evidence
- emit decision event with request_id + policy_hash
