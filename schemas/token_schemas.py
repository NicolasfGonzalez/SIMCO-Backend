from pydantic import BaseModel
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str
    id_user: UUID
    id_role: int

class TokenPayload(BaseModel):
    sub: str | None = None