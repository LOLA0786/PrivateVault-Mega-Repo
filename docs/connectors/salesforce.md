# PrivateVault Salesforce Connector – Design Specification (v1)

## 1) Overview
Goal: A native Salesforce app that ingests deal/context data, submits governed actions to PrivateVault, supports approvals, and surfaces audit/evidence to users.

**User Roles**
1. Sales Ops / RevOps: configures field mappings and policies.
2. Approvers (CRO/Legal/Finance/DPO): approve governed actions.
3. Auditors / Compliance: view audit and evidence bundles.

## 2) Architecture

**High-Level Flow**
1. Salesforce Opportunity update → Connector extracts context.
2. Connector signs context and creates approval requirements.
3. Connector sends action request to PrivateVault API.
4. PrivateVault enforces quorum and logs audit.
5. Salesforce UI shows approval status and audit evidence.

**Components**
- Salesforce Managed Package
  - Apex service
  - Lightning UI components
  - Permission sets
  - Custom objects for approvals and audit references
- PrivateVault API
  - `/api/v1/actions/emit/{domain}`
  - `/api/v1/quorum/validate`
  - `/api/v1/approvals`
  - `/api/v1/audit`
  - `/api/v1/evidence/export`
- Optional Middleware (Phase‑2)
  - Batched processing and retries
  - Token refresh and bulk exports

## 3) Auth Model

**Service Token Auth (Phase‑1)**
- Salesforce Named Credential stores a PrivateVault service token.
- Scope-limited tokens:
  - `actions:emit`, `quorum:read`, `approvals:read`, `audit:read`, `evidence:export`.
- Token stored only in Salesforce credential store (not in objects).

**Phase‑2**
- OAuth2/SAML for user-level authorization.
- Support for per-user approvals tied to PrivateVault roles.

## 4) Data Mapping

**Primary Objects**
- Opportunity → `deal_context`
- Account → `customer_context`
- Contact → `counterparty_context`
- Product / Line Item → `transaction_context`

**Mapping Example**
| Salesforce Field | PrivateVault Context Field |
|------------------|----------------------------|
| Opportunity.Amount | `amount` |
| Opportunity.StageName | `stage` |
| Account.Industry | `industry` |
| Account.BillingCountry | `region` |
| Contact.Email | `counterparty_email` |
| Opportunity.OwnerId | `actor_id` |

**Context Payload Example**
```json
{
  "tenant_id": "tenant-demo",
  "actor_id": "sf-user-123",
  "action": "approve_discount",
  "amount": 100000,
  "region": "US",
  "stage": "Negotiation",
  "counterparty_email": "buyer@corp.com"
}
```

## 5) Approval Handling

**Approval Lifecycle**
1. Salesforce triggers action submission.
2. PrivateVault evaluates quorum rules.
3. If approvals required:
   - Creates approval records
   - Returns pending status to Salesforce
4. Salesforce Approval object tracks status and approvers.
5. Approvers can approve in Salesforce, which:
   - Signs approval context
   - Submits to PrivateVault `/api/v1/approvals`

**Approval Roles**
- CRO, Legal, Finance, DPO, etc.
- Mapped from Salesforce Profile/Role → PrivateVault role.

## 6) Audit and Evidence

**Audit**
- Salesforce UI fetches audit events:
  - `/api/v1/audit?tenant_id=...`
- Display audit history by Opportunity ID or Account ID.
- Include decision, policy, quorum, and timestamps.

**Evidence**
- Evidence bundle export initiated from Salesforce UI.
- `/api/v1/evidence/export`
- Bundle is stored in PrivateVault export root and referenced in Salesforce.

## 7) Deployment Model

**Phase‑1: Managed Package**
- Installed in Salesforce org.
- Configurable Named Credential to PrivateVault API.
- Admin configuration for field mappings and tenant ID.

**Phase‑2: External Middleware**
- Optional PrivateVault connector service.
- Provides batching, retries, and audit aggregation.
- Supports multi‑org deployments.

## 8) Security Review

**Data Protection**
- All requests signed.
- No secrets stored in Salesforce objects.
- Context signed per request.

**Scope and Access**
- Service token scopes restricted.
- Salesforce permission sets for connector access.

**Audit Trail**
- PrivateVault logs all actions.
- Salesforce stores event references, not raw audit logs.

**Compliance**
- Evidence exports traceable to Opportunity IDs.
- Approvals bound to decision records.

## 9) Packaging Plan

**Managed Package Contents**
- Apex classes (connector client)
- Lightning components for:
  - Approval status
  - Audit history
  - Evidence export
- Custom objects:
  - `PV_Approval__c`
  - `PV_AuditRef__c`
  - `PV_Config__c`
- Permission sets:
  - `PrivateVault Admin`
  - `PrivateVault Approver`

**Release Phases**
1. Alpha: internal orgs.
2. Beta: select customers.
3. GA: AppExchange listing.
