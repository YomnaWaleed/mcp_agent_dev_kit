from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    customer_id: Optional[int] = None


class AuthRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AgentResponse(BaseModel):
    status: str
    response: str
    data: Optional[dict] = None
