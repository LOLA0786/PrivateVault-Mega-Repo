import test from 'node:test';
import assert from 'node:assert/strict';

import { Client } from '../src/client.js';
import { createApproval } from '../src/approvals.js';
import { verifyManifest } from '../src/verify.js';


test('client adds auth header', async () => {
  const client = new Client({ baseUrl: 'http://localhost:8000/api/v1', token: 't' });
  const originalFetch = global.fetch;
  global.fetch = async (url, opts) => {
    assert.equal(opts.headers.Authorization, 'Bearer t');
    return { status: 200, ok: true, json: async () => ({ status: 'ok' }) };
  };
  await client.request('GET', '/status');
  global.fetch = originalFetch;
});

test('approval signature', () => {
  const approval = createApproval({
    approverId: 'a',
    role: 'CRO',
    region: 'US',
    intentHash: 'ih',
    keyId: 'k1',
    secret: 'secret',
  });
  assert.ok(approval.signature);
});

test('verify manifest missing', () => {
  const result = verifyManifest('/tmp/does-not-exist');
  assert.equal(result.valid, false);
  assert.ok(result.mismatches.includes('MANIFEST_MISSING'));
});
