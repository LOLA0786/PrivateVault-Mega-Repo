from collections import defaultdict
from datetime import datetime

USAGE = defaultdict(list)

def record_usage(api_key: str, tenant_id: str, path: str, status: int):
    USAGE[api_key].append({
        "tenant_id": tenant_id,
        "path": path,
        "status": status,
        "ts": datetime.utcnow().isoformat(),
    })

def get_usage(api_key: str):
    return USAGE.get(api_key, [])
