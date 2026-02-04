export class RetryConfig {
  constructor({ attempts = 3, backoffSeconds = 0.25, retryStatuses = [429, 500, 502, 503, 504] } = {}) {
    this.attempts = attempts;
    this.backoffSeconds = backoffSeconds;
    this.retryStatuses = retryStatuses;
  }
}

export async function backoffSleep(attempt, baseSeconds) {
  const delay = baseSeconds * Math.pow(2, attempt - 1);
  await new Promise((resolve) => setTimeout(resolve, delay * 1000));
}
