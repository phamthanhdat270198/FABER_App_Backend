from pydantic import BaseModel
from typing import Optional

class PaintTypeBase(BaseModel):
    paint_type: str
    mo_ta_san_pham: str = ""
    thanh_phan: str = ""
    huong_dan_su_dung: str = ""
    luu_y: Optional[str] = None
    bao_quan: str = ""
    is_active: bool = True

class PaintTypeCreate(PaintTypeBase):
    pass

class PaintTypeUpdate(BaseModel):
    paint_type: Optional[str] = None
    mo_ta_san_pham: Optional[str] = None
    thanh_phan: Optional[str] = None
    huong_dan_su_dung: Optional[str] = None
    luu_y: Optional[str] = None
    bao_quan: Optional[str] = None
    is_active: Optional[bool] = None

class PaintTypeResponse(PaintTypeBase):
    id: int
    
    class Config:
        orm_mode = True