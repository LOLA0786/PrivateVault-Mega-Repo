export async function exportEvidence(client, { tenantId, start, end, bundleName, idempotencyKey }) {
  const body = { tenant_id: tenantId, start, end };
  if (bundleName) {
    body.bundle_name = bundleName;
  }
  const resp = await client.request('POST', '/evidence/export', {
    jsonBody: body,
    idempotencyKey,
  });
  if (!resp.ok) {
    throw new Error(`evidence export failed: ${resp.status}`);
  }
  return resp.json();
}
