# Authority Registry — DESIGN

## Purpose
Declare *who has authority* to execute governance actions in a given scope.

## Contract
Input:
- subject (user/serviceaccount/group)
- roles: Owner | Approver | Auditor | IncidentCommander
- scope: env + system
Output:
- resolved roles for subject/scope

## Invariants
- Role assignment is explicit and auditable.
- Expired bindings do not grant access.

## Failure Modes
- registry unavailable -> deny closure actions
- no binding -> deny

## Evidence
- AuthorityBinding CRD objects act as system-of-record
