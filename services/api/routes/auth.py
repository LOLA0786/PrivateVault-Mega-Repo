from fastapi import APIRouter, Depends

from services.api.middleware.auth import AuthContext, require_auth
from services.api.models import AuthToken

router = APIRouter()


@router.get("/auth/me", response_model=AuthToken)
def auth_me(auth: AuthContext = Depends(require_auth)):
    return {"token": auth.token, "scopes": auth.scopes, "tenant_id": auth.tenant_id}
