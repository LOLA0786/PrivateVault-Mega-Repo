# Reference Connector Implementations (v1)

## 1) OpenAI Connector (AI Domain) – Reference Implementation Plan

### Directory / Module Layout
```
connectors/
  ai/
    openai/
      connector.json
      connector.py
      schemas/
        model_invoke.json
        tool_call.json
      config/
        openai.defaults.json
      docs/
        README.md
```

### Manifest Example (`connector.json`)
```json
{
  "id": "pv.ai.openai",
  "name": "OpenAI Connector",
  "version": "1.0.0",
  "domain": "ai",
  "publisher": "PrivateVault",
  "entrypoint": "connectors/ai/openai/connector.py",
  "capabilities": [
    {
      "action": "model_invoke",
      "schema": "schemas/model_invoke.json",
      "quorum_policy": "AI_SENSITIVE",
      "idempotency": true
    },
    {
      "action": "tool_call",
      "schema": "schemas/tool_call.json",
      "quorum_policy": "AI_TOOL",
      "idempotency": true
    }
  ],
  "auth": {
    "type": "vault",
    "scopes": ["ai:invoke"]
  },
  "audit": {
    "required": true,
    "events": ["request", "decision", "execution", "error"]
  },
  "signing": {
    "required": true,
    "publisher_key_id": "pv-key-001"
  }
}
```

### Auth Handling
- Type: `vault` (PrivateVault fetches OpenAI API key from KMS/Vault).
- Connector never stores secrets, receives credentials at runtime.
- Scopes enforced: `ai:invoke`.

### Context Signing Flow
1. Client submits signed context to PrivateVault API.
2. PrivateVault verifies signature.
3. Connector uses validated context to build OpenAI request.

### Quorum Enforcement Points
- Pre‑execution: PrivateVault quorum check enforced before connector `execute`.
- Quorum policy from manifest: `AI_SENSITIVE`, `AI_TOOL`.

### Audit Hook Integration
- `on_request`: log normalized model request metadata.
- `on_decision`: log quorum result + policy version.
- `on_execution`: log model response metadata (no raw secrets).
- `on_error`: log error codes and sanitized context.

### Error / Retry Handling
- Retriable: 429 / 5xx → retry with exponential backoff.
- Non‑retriable: 4xx auth errors → fail fast.
- All errors logged via audit hooks.

### Configuration Format
`config/openai.defaults.json`
```json
{
  "model": "gpt-4o-mini",
  "timeout_seconds": 30,
  "max_retries": 3
}
```

### Test Strategy
1. Unit tests
   - Manifest validation
   - Context signing check
   - Auth injection
2. Integration tests
   - Mock OpenAI API
   - Quorum enforcement path
3. Compliance regression
   - Audit hooks always invoked
   - No raw secrets in logs

### Security Boundaries
- No raw API keys in connector code.
- No direct network access outside OpenAI endpoints.
- Quorum enforced before any call.
- Audit required for every execution.

---

## 2) Salesforce Connector (CRM Domain) – Reference Implementation Plan

### Directory / Module Layout
```
connectors/
  crm/
    salesforce/
      connector.json
      adapter/
        apex/
        lightning/
      config/
        mapping.json
        defaults.json
      docs/
        README.md
```

### Manifest Example (`connector.json`)
```json
{
  "id": "pv.crm.salesforce",
  "name": "Salesforce Connector",
  "version": "1.0.0",
  "domain": "crm",
  "publisher": "PrivateVault",
  "entrypoint": "connectors/crm/salesforce/adapter",
  "capabilities": [
    {
      "action": "deal_submit",
      "schema": "schemas/crm/deal_context.json",
      "quorum_policy": "CRM_HIGH_RISK",
      "idempotency": true
    },
    {
      "action": "approval_submit",
      "schema": "schemas/crm/approval.json",
      "quorum_policy": "CRM_APPROVAL",
      "idempotency": true
    }
  ],
  "auth": {
    "type": "oauth",
    "scopes": ["crm:read", "crm:write"]
  },
  "audit": {
    "required": true,
    "events": ["request", "decision", "execution", "error"]
  },
  "signing": {
    "required": true,
    "publisher_key_id": "pv-key-001"
  }
}
```

### Auth Handling
- Salesforce side: Named Credential (service token to PrivateVault).
- PrivateVault side: service token scopes:
  - `actions:emit`, `quorum:read`, `approvals:read`, `audit:read`, `evidence:export`.
- OAuth for Salesforce API access.

### Context Signing Flow
1. Salesforce captures deal context.
2. Connector signs context using PrivateVault signing helper.
3. Signed context sent to PrivateVault `/api/v1/actions/emit/{domain}`.

### Quorum Enforcement Points
- Pre‑execution: PrivateVault checks quorum before approving deal submit.
- Approval actions routed through `/api/v1/approvals` once Salesforce user approves.

### Audit Hook Integration
- `on_request`: log CRM record id + tenant id.
- `on_decision`: log quorum results.
- `on_execution`: log action result and CRM response.
- `on_error`: log error summary and CRM record reference.

### Error / Retry Handling
- CRM API failures → retry with backoff.
- PrivateVault 429/5xx → retry.
- Non‑retriable errors → deadletter queue in connector middleware.

### Configuration Format
`config/mapping.json`
```json
{
  "Opportunity.Amount": "amount",
  "Opportunity.StageName": "stage",
  "Account.Industry": "industry",
  "Account.BillingCountry": "region",
  "Contact.Email": "counterparty_email",
  "Opportunity.OwnerId": "actor_id"
}
```

`config/defaults.json`
```json
{
  "tenant_id": "tenant-demo",
  "region": "US"
}
```

### Test Strategy
1. Unit tests
   - Field mapping engine
   - Context signing payloads
   - Approval submission structure
2. Integration tests
   - Mock Salesforce API
   - Quorum enforcement flow
   - Audit log synchronization
3. Compliance regression
   - Evidence export references in CRM
   - Audit hook coverage

### Security Boundaries
- No secrets stored in Salesforce objects.
- Service tokens stored in Named Credential.
- Signed context enforced before submission.
- Approvals bound to PrivateVault decision record.
