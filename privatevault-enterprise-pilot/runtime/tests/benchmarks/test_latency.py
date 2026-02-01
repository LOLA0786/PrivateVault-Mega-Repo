import time
from galani.crypto.selector import get_crypto_backend


def test_crypto_latency():
    backend = get_crypto_backend()
    start = time.time()
    backend.sign(b"galani")
    latency_ms = (time.time() - start) * 1000

    assert latency_ms < 10  # hard budget
