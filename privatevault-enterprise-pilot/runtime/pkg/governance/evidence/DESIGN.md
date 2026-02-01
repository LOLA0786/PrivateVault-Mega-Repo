# Evidence Pack — DESIGN

## Purpose
Export audit-grade proof of events, authority, and closure.

## Contract
Input:
- CaseFile + lineage chain head hash
Output:
- ZIP evidence pack:
  - evidence.json
  - compliance.json
  - summary.txt

## Invariants
- Pack must include final chain head hash
- GeneratedAt UTC
- Deterministic export given same inputs
