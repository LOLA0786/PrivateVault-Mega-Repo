from fastapi import Request
from typing import Optional

def resolve_tenant(request: Request) -> Optional[str]:
    """
    Tenant is derived directly from API key.
    Auto-create behavior handled elsewhere.
    """
    return getattr(request.state, "tenant_id", None)
