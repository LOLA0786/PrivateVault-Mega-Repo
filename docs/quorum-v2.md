# Quorum v2 Operator Guide

This guide describes how to configure and operate the Quorum v2 approval engine with per-tenant rules, per-action rules, role and region constraints, expiry, revocation, and audit binding. It is backward compatible with v1 and supports a no-downtime migration path.

**Overview**
Quorum v2 supports:
1. Per-tenant defaults and per-action overrides
2. Role-based requirements (CRO, Legal, Finance, DPO, etc.)
3. Optional regional constraints (APAC, EU, US)
4. Approval expiry and revocation
5. Audit binding via `rule_id` and `approvals_used` in audit events

**Configuration Sources**
Quorum v2 rules can be provided by:
1. `PV_QUORUM_RULES_V2` (JSON string)
2. `PV_QUORUM_RULES_YAML` (YAML string, requires `PyYAML`)
3. `PV_QUORUM_RULES_FILE` (path to JSON or YAML file)

Legacy configuration remains supported:
1. `PV_QUORUM_RULES` for per-action min approvals
2. `PV_QUORUM_MIN` for default min approvals

**Example Quorum v2 JSON Config**
```json
{
  "defaults": {
    "min_approvals": 2
  },
  "actions": {
    "POST /api/emit/medtech": {
      "min_approvals": 2,
      "roles_required": ["DPO"],
      "approver_regions": ["EU"]
    }
  },
  "tenants": {
    "tenant-1": {
      "defaults": {
        "min_approvals": 3,
        "roles_required": ["CRO", "Legal"]
      },
      "actions": {
        "POST /api/emit/fintech": {
          "min_approvals": 3,
          "roles_required": ["CRO", "Legal"],
          "roles_optional": ["Finance"],
          "approver_regions": ["US", "EU"],
          "require_approval_id": true,
          "max_approvals_age_seconds": 1800,
          "rule_id": "tenant-1-fintech"
        }
      }
    }
  }
}
```

**Example Quorum v2 YAML Config**
```yaml
defaults:
  min_approvals: 2
actions:
  POST /api/emit/medtech:
    min_approvals: 2
    roles_required:
      - DPO
    approver_regions:
      - EU
tenants:
  tenant-1:
    defaults:
      min_approvals: 3
      roles_required:
        - CRO
        - Legal
    actions:
      POST /api/emit/fintech:
        min_approvals: 3
        roles_required:
          - CRO
          - Legal
        roles_optional:
          - Finance
        approver_regions:
          - US
          - EU
        require_approval_id: true
        max_approvals_age_seconds: 1800
        rule_id: tenant-1-fintech
```

**Per-Tenant and Per-Action Rules**
Rule resolution order:
1. Tenant + action
2. Tenant defaults
3. Global action
4. Global defaults
5. Legacy v1 rules (`PV_QUORUM_RULES`, `PV_QUORUM_MIN`)

Per-tenant overrides allow you to enforce stricter rules for specific tenants without affecting others.

**Example Signed Approval Payloads**
Approval objects are provided in the `X-PV-Approvals` header as a JSON array.

Minimum v1-compatible approval:
```json
{
  "approver_id": "approver-1",
  "key_id": "k1",
  "signature": "hmac(intent_hash)",
  "intent_hash": "e3b0c44298fc..."
}
```

Recommended v2 approval:
```json
{
  "approval_id": "APP-1234",
  "approver_id": "approver-1",
  "role": "CRO",
  "region": "US",
  "key_id": "k1",
  "signature": "hmac(intent_hash)",
  "intent_hash": "e3b0c44298fc...",
  "issued_at": 1736000000,
  "expires_at": 1736003600
}
```

**Migration Path from v1 to v2 (No Downtime)**
1. Keep existing `PV_QUORUM_RULES` and `PV_QUORUM_MIN` in place.
2. Add `PV_QUORUM_RULES_V2` or `PV_QUORUM_RULES_FILE` with minimal defaults.
3. Roll out v2 rules tenant-by-tenant by adding entries under `tenants`.
4. Begin emitting v2 approvals with role and region data.
5. Enable `require_approval_id` and `max_approvals_age_seconds` once clients supply those fields.
6. Remove legacy env variables after all tenants are migrated and validated.

**Common Misconfigurations and Errors**
1. `QUORUM_RULES_INVALID`: JSON/YAML is malformed or not an object.
2. `QUORUM_YAML_UNAVAILABLE`: `PV_QUORUM_RULES_YAML` or YAML file used without `PyYAML` installed.
3. `QUORUM_MIN_INVALID`: `min_approvals` is not an integer.
4. `QUORUM_ROLE_MISSING`: Required roles were not present in approvals.
5. `QUORUM_NOT_MET`: Total valid approvals did not meet `min_approvals`.
6. `APPROVAL_SIGNATURE_INVALID`: Signature does not match the `intent_hash`.
7. `QUORUM_REVOKED_IDS_INVALID`: `PV_QUORUM_REVOKED_IDS` is not a JSON list.
8. `APPROVALS_INVALID`: `X-PV-Approvals` is not a JSON array.

**Operational Notes**
1. Use `PV_QUORUM_REVOKED_IDS` to invalidate approvals by `approval_id`.
2. `max_approvals_age_seconds` requires `issued_at` on approvals.
3. Role enforcement only applies if `roles_required` or `roles_optional` are configured.
4. Region enforcement only applies if `approver_regions` is configured.
