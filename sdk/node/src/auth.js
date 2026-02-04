export async function authMe(client) {
  const resp = await client.request('GET', '/auth/me');
  if (!resp.ok) {
    throw new Error(`auth_me failed: ${resp.status}`);
  }
  return resp.json();
}
