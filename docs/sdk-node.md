# PrivateVault SDK v1 (Node)

This SDK wraps API v1 and provides helpers for context signing, approvals, quorum validation, and evidence export.

## Install (local)
```bash
node -e "import('./sdk/node/src/index.js').then(m => console.log(Object.keys(m)))"
```

## Usage
```js
import { Client, createApproval, validateQuorum, exportEvidence } from './sdk/node/src/index.js';

const client = new Client({ baseUrl: 'http://localhost:8000/api/v1', token: 'TOKEN' });

const payload = { amount: 100, recipient: 'acct-1' };
const intentHash = '<hash>';

const approval = createApproval({
  approverId: 'approver-1',
  role: 'CRO',
  region: 'US',
  intentHash,
  keyId: 'k1',
  secret: 'secret-1',
});

await validateQuorum(client, { action: 'POST /api/emit/fintech', payload, approvals: [approval] });

await exportEvidence(client, {
  tenantId: 'tenant-demo',
  start: '2026-02-01T00:00:00Z',
  end: '2026-02-28T23:59:59Z',
});
```

## OpenAPI Types
- Spec: `sdk/openapi/openapi.json`
- Generator script: `scripts/sdk/generate_node_types.sh`

## Notes
- Tokens are stored in memory only.
- Automatic retries on 429/5xx.
- Idempotency supported for export.
