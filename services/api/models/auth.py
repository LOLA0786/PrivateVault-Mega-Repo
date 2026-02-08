from pydantic import BaseModel

class AuthToken(BaseModel):
    token: str
    scopes: list[str] = []
    tenant_id: str | None = None
