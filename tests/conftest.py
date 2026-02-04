import os
import tempfile

import pytest


def _set_default_env(key: str, value: str) -> None:
    if not os.getenv(key):
        os.environ[key] = value


@pytest.fixture(scope="session", autouse=True)
def _test_env_session():
    # Ensure test environment defaults are always set.
    _set_default_env("PV_ENV", "test")
    _set_default_env("PV_CONTEXT_KEYS", "{\"k1\":\"test-secret\"}")
    _set_default_env("PV_QUORUM_MIN", "2")

    storage_dir = os.getenv("PV_STORAGE_PATH")
    storage_tmp = None
    if not storage_dir:
        storage_tmp = tempfile.TemporaryDirectory(prefix="pv_test_storage_")
        storage_dir = storage_tmp.name
        os.environ["PV_STORAGE_PATH"] = storage_dir

    audit_path = os.getenv("PV_AUDIT_LOG_PATH")
    audit_tmp = None
    if not audit_path:
        audit_tmp = tempfile.NamedTemporaryFile(prefix="pv_test_audit_", suffix=".log", delete=False)
        audit_path = audit_tmp.name
        audit_tmp.close()
        os.environ["PV_AUDIT_LOG_PATH"] = audit_path

    # Ensure audit file exists before tests.
    if audit_path and not os.path.exists(audit_path):
        open(audit_path, "a").close()

    yield

    # Cleanup after session.
    if audit_tmp and audit_path and os.path.exists(audit_path):
        try:
            os.remove(audit_path)
        except Exception:
            pass
    if storage_tmp:
        storage_tmp.cleanup()
