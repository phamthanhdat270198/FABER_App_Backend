from pydantic import BaseModel
from typing import Optional

class PaintTypeBase(BaseModel):
    paint_type: str
    description: Optional[str] = None

class PaintTypeCreate(PaintTypeBase):
    pass

class PaintTypeUpdate(BaseModel):
    paint_type: Optional[str] = None
    description: Optional[str] = None

class PaintTypeResponse(PaintTypeBase):
    id: int
    
    class Config:
        orm_mode = True