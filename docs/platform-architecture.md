# PrivateVault Enterprise Platform Architecture

## Table of Contents
1. Architecture Blueprint
2. API v1 Surface
3. CLI and SDK Plan
4. Integration Strategy
5. Testing Matrix
6. Ops and Compliance Roadmap
7. 90-Day Plan
8. Implementation Plan

## 1) Architecture Blueprint

### Guiding Principles
1. Security-first: signed contexts, strict tenant scoping, mandatory audit, quorum enforcement.
2. Enterprise operability: observable, debuggable, reproducible evidence bundles.
3. Versioned APIs: forward-compatible with explicit deprecation policy.
4. Pluggable integrations: Kafka-compatible event streaming abstraction.
5. Residency-ready: schema includes region and locale tagging.

### Core Components
1. API Gateway
   - `/api/v1` routing and versioning
   - Auth (service tokens + scopes)
   - Rate limiting and idempotency
   - Tenant isolation middleware
2. Policy and Quorum Service
   - Policy registry and activation
   - Quorum engine with role and region constraints
   - Approval storage and verification
3. Audit and Evidence Service
   - Structured audit logging
   - Evidence export bundles with verifiable hashes
4. Decision Ledger (optional Phase-1, required Phase-2)
   - Hash-chained decision records
   - Evidence binding and verification
5. Integrations Hub
   - Webhooks with retry and signature verification
   - Event streaming abstraction (Kafka-compatible first)
   - Connector framework (Salesforce, HubSpot, Zoho)
6. Operator CLI
   - `pv` commands for tenant, quorum, evidence, and status
   - Secure credential handling
7. SDKs
   - Python and Node generated from OpenAPI
   - Context signing and approval helpers

### Request Flow
1. Authenticate request with service token and scopes.
2. Resolve tenant and enforce isolation.
3. Validate signed context (required).
4. Enforce idempotency (mutating endpoints).
5. Evaluate quorum rules for gated actions.
6. Execute action.
7. Emit audit event with evidence binding.
8. Publish event to streaming/webhook sinks.

## 2) API v1 Surface

### Base
- `GET /api/v1/status`
- `GET /api/v1/health`

### Auth
- `POST /api/v1/auth/token`
- `GET /api/v1/auth/me`

### Tenants
- `POST /api/v1/tenants`
- `GET /api/v1/tenants/{tenant_id}`
- `PATCH /api/v1/tenants/{tenant_id}`

### Policies
- `POST /api/v1/policies`
- `GET /api/v1/policies`
- `GET /api/v1/policies/{version}`
- `POST /api/v1/policies/{version}/activate`

### Quorum and Approvals
- `POST /api/v1/approvals`
- `GET /api/v1/approvals`
- `POST /api/v1/quorum/validate`
- `GET /api/v1/quorum/rules`
- `PUT /api/v1/quorum/rules`

### Audit and Evidence
- `GET /api/v1/audit`
- `GET /api/v1/audit/{event_id}`
- `POST /api/v1/evidence/export`
- `GET /api/v1/evidence/{bundle_id}`

### Decisions and Actions
- `POST /api/v1/actions/emit/{domain}`

### Integrations
- `POST /api/v1/webhooks`
- `GET /api/v1/webhooks`
- `POST /api/v1/events/stream`

### Platform Metadata
- `GET /api/v1/openapi.json`

### Cross-Cutting Requirements
1. Auth: service tokens with scopes (`audit:read`, `policy:write`, `quorum:manage`, `evidence:export`).
2. Tenant isolation: tenant-bound tokens or `X-PV-Tenant`.
3. Idempotency: `Idempotency-Key` required for mutating endpoints.
4. Rate limits: token- and tenant-based.
5. Audit: mandatory audit logging for every endpoint.

## 3) CLI and SDK Plan

### Operator CLI (`pv`)
- `pv init`
- `pv login`
- `pv tenant create|get|list`
- `pv quorum set|get|validate`
- `pv approvals create|list|revoke`
- `pv policies register|activate|list`
- `pv audit export|tail`
- `pv evidence export|get`
- `pv demo bootstrap|reset`
- `pv status`

### CLI Design
1. Built on top of the Public Platform APIs.
2. Output formats:
   - Human-readable tables by default.
   - `--format=json` for automation.
3. Secure credential handling:
   - OS keychain if available.
   - Encrypted file fallback.

### SDKs
1. Python and Node SDKs generated from OpenAPI.
2. Helpers:
   - Context signing and verification
   - Approval creation and submission
   - Evidence export orchestration

## 4) Integration Strategy

### Phase-1
1. Event streaming abstraction with Kafka-compatible interface.
2. Webhook delivery with retry, backoff, and signatures.
3. Connector scaffolding for Salesforce/HubSpot/Zoho (config and auth placeholders).

### Phase-2
1. Fully supported Salesforce, HubSpot, Zoho connectors.
2. Replay and dead-letter queues.
3. SaaS billing and usage tracking integration.

## 5) Testing Matrix

### Unit
1. Auth and scopes
2. Tenant isolation
3. Quorum rules evaluation
4. Audit logging
5. Evidence export

### Integration
1. Full request flow (auth → quorum → audit → evidence).
2. Idempotency and rate limiting.
3. Webhook delivery and retry.

### Load and Failure Simulation
1. Rate limit enforcement under load.
2. Quorum timeouts and approval bursts.
3. Evidence export at scale.

### Compliance Regression
1. Evidence bundle reproducibility.
2. Hash verification.
3. Policy activation history integrity.

## 6) Ops and Compliance Roadmap

### Phase-1
1. Single-region SaaS deployment.
2. Shared DB with strict tenant scoping.
3. Audit and evidence export with verifiable hashes.
4. Manual key rotation.

### Phase-2
1. Multi-region (EU/US) residency controls.
2. SAML/OIDC enterprise identity.
3. HSM/KMS integration.
4. Evidence bundle signing.

### Phase-3
1. Hard isolation (per-tenant DB/queue).
2. Advanced compliance reporting.
3. Mandatory decision ledger enforcement.

## 7) 90-Day Plan

### Month 1
1. API v1 skeleton and auth.
2. Tenant isolation middleware.
3. Quorum rules service with persistence.
4. Audit logging enforcement.

### Month 2
1. Evidence export bundles.
2. CLI MVP.
3. SDK generation pipeline.
4. Full OpenAPI spec.

### Month 3
1. Integration interface and webhooks.
2. Load testing and compliance regression.
3. Beta readiness review.

## 8) Implementation Plan

### Repo Structure
- `services/api` (gateway and routing)
- `services/quorum`
- `services/audit`
- `services/evidence`
- `cli/`
- `sdk/python`
- `sdk/node`
- `docs/`

### Module Ownership
1. API team: gateway, auth, tenancy.
2. Compliance team: audit and evidence.
3. Integrations team: webhooks and connectors.
4. Platform team: CLI, SDKs, and tests.

### Test Strategy
1. Unit tests per service.
2. Integration tests via docker-compose.
3. Load tests using k6 or Locust.
