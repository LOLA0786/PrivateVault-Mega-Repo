import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _audit_log_env_session():
    path = os.getenv("PV_AUDIT_LOG_PATH") or "/tmp/pv_test_audit.log"
    if not os.getenv("PV_AUDIT_LOG_PATH"):
        os.environ["PV_AUDIT_LOG_PATH"] = path
    # Ensure file exists before tests
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        open(path, "a").close()
    yield
    # Cleanup after session
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
