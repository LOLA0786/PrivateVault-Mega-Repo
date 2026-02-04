import { Client, createApproval, validateQuorum, exportEvidence } from '../src/index.js';

const client = new Client({ baseUrl: 'http://localhost:8000/api/v1', token: 'YOUR_TOKEN' });

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
