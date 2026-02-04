import crypto from 'crypto';

export function computeRequestHash(method, pathWithQuery, bodyBuffer) {
  const hash = crypto.createHash('sha256');
  hash.update(method.toUpperCase());
  hash.update('\n');
  hash.update(pathWithQuery);
  hash.update('\n');
  if (bodyBuffer) {
    hash.update(bodyBuffer);
  }
  return hash.digest('hex');
}

export function signContext(context, secret) {
  const payload = JSON.stringify(context, Object.keys(context).sort());
  return crypto.createHmac('sha256', secret).update(payload).digest('hex');
}
