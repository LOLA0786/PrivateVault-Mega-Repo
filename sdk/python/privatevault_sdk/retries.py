import time
from dataclasses import dataclass
from typing import Iterable


@dataclass
class RetryConfig:
    attempts: int = 3
    backoff_seconds: float = 0.25
    retry_statuses: Iterable[int] = (429, 500, 502, 503, 504)


def backoff_sleep(attempt: int, base: float) -> None:
    time.sleep(base * (2 ** (attempt - 1)))
