import os

import pytest


@pytest.fixture(autouse=True)
def _audit_log_env():
    if not os.getenv("PV_AUDIT_LOG_PATH"):
        os.environ["PV_AUDIT_LOG_PATH"] = "/tmp/pv_test_audit.log"
    yield
