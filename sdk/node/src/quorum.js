export async function validateQuorum(client, { action, payload, approvals, tenantId }) {
  const body = { action, payload, approvals };
  if (tenantId) {
    body.tenant_id = tenantId;
  }
  const resp = await client.request('POST', '/quorum/validate', { jsonBody: body });
  if (!resp.ok) {
    throw new Error(`quorum validate failed: ${resp.status}`);
  }
  return resp.json();
}
