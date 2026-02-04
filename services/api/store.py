from typing import Dict, Optional, Any

from services.api.models import TenantResponse


_TENANTS: Dict[str, TenantResponse] = {}
_QUORUM_RULES: Optional[dict] = None


def list_tenants():
    return list(_TENANTS.values())


def get_tenant(tenant_id: str):
    return _TENANTS.get(tenant_id)


def create_tenant(tenant: TenantResponse):
    _TENANTS[tenant.tenant_id] = tenant
    return tenant


def update_tenant(tenant_id: str, updates: dict):
    existing = _TENANTS.get(tenant_id)
    if not existing:
        return None
    data = existing.model_dump()
    data.update({k: v for k, v in updates.items() if v is not None})
    updated = TenantResponse(**data)
    _TENANTS[tenant_id] = updated
    return updated


def delete_tenant(tenant_id: str):
    return _TENANTS.pop(tenant_id, None)


def get_quorum_rules() -> Optional[dict]:
    return _QUORUM_RULES


def set_quorum_rules(rules: dict) -> dict:
    global _QUORUM_RULES
    _QUORUM_RULES = rules
    return _QUORUM_RULES
