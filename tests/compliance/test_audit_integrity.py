import os

def test_audit_file_exists():
    path = os.environ.get("PV_AUDIT_LOG_PATH")
    assert path is not None
    assert os.path.exists(path)
