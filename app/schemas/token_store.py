from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TokenStoreBase(BaseModel):
    user_id: int
    token: str
    device_info: Optional[str] = None

class TokenStoreCreate(TokenStoreBase):
    expires_at: datetime

class TokenStoreResponse(TokenStoreBase):
    id: int
    expires_at: datetime
    created_at: datetime
    last_used_at: datetime
    is_revoked: bool
    
    class Config:
        orm_mode = True