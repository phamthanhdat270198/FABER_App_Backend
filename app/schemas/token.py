from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_at: datetime

class TokenPayload(BaseModel):
    sub: Optional[int] = None