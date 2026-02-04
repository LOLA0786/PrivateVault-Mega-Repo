import os


def test_audit_file_exists():
    path = os.getenv("PV_AUDIT_LOG_PATH")
    assert path, "PV_AUDIT_LOG_PATH must be set"
    assert os.path.exists(path), "Audit log file must exist"
