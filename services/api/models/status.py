from typing import Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class StatusResponse(BaseModel):
    status: str
    version: Optional[str]
