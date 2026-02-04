import { RetryConfig, backoffSleep } from './retries.js';

export class Client {
  constructor({ baseUrl, token, retry, timeoutSeconds = 30 } = {}) {
    this.baseUrl = (baseUrl || '').replace(/\/$/, '');
    this.token = token || null;
    this.retry = retry || new RetryConfig();
    this.timeoutSeconds = timeoutSeconds;
  }

  setToken(token) {
    this.token = token;
  }

  _headers(idempotencyKey) {
    const headers = { Accept: 'application/json' };
    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }
    if (idempotencyKey) {
      headers['Idempotency-Key'] = idempotencyKey;
    }
    return headers;
  }

  async request(method, path, { jsonBody, params, idempotencyKey } = {}) {
    const url = new URL(`${this.baseUrl}/${path.replace(/^\//, '')}`);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.set(key, value);
        }
      });
    }

    let lastError;
    for (let attempt = 1; attempt <= this.retry.attempts; attempt += 1) {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), this.timeoutSeconds * 1000);
        const response = await fetch(url.toString(), {
          method,
          headers: this._headers(idempotencyKey),
          body: jsonBody ? JSON.stringify(jsonBody) : undefined,
          signal: controller.signal,
        });
        clearTimeout(timeout);
        if (this.retry.retryStatuses.includes(response.status) && attempt < this.retry.attempts) {
          await backoffSleep(attempt, this.retry.backoffSeconds);
          continue;
        }
        return response;
      } catch (err) {
        lastError = err;
        if (attempt >= this.retry.attempts) {
          throw err;
        }
        await backoffSleep(attempt, this.retry.backoffSeconds);
      }
    }
    if (lastError) {
      throw lastError;
    }
    return undefined;
  }
}
