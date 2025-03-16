from pydantic import BaseModel
from typing import Optional

class TypeDetailBase(BaseModel):
    paint_type_id: int
    product: str
    code: Optional[str] = None
    package: Optional[str] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    m2_cover: Optional[float] = None
    promotion: Optional[str] = None
    base64: Optional[str] = None
    is_active: bool = True

class TypeDetailCreate(TypeDetailBase):
    pass

class TypeDetailUpdate(BaseModel):
    paint_type_id: Optional[int] = None
    product: Optional[str] = None
    code: Optional[str] = None
    package: Optional[str] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    m2_cover: Optional[float] = None
    promotion: Optional[str] = None
    base64: Optional[str] = None
    is_active: bool = True

class TypeDetailResponse(TypeDetailBase):
    id: int
    
    class Config:
        orm_mode = True

class TypeDetailWithPaintType(TypeDetailResponse):
    paint_type_name: str
    
    class Config:
        orm_mode = True