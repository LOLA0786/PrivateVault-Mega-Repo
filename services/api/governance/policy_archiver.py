from pathlib import Path
from datetime import datetime
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent.parent
POLICY_STORE = BASE_DIR / "policy_store" / "tenants"
ARCHIVE_DIR = BASE_DIR / "policy_store" / "archive"

ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def archive_policy(policy_name: str):
    src = POLICY_STORE / policy_name
    if not src.exists():
        return None

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archived_name = f"{policy_name.replace('.yaml','')}-{ts}.yaml"
    dst = ARCHIVE_DIR / archived_name

    shutil.copy2(src, dst)
    return dst
