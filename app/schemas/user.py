from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    ho_ten: str
    dia_chi: Optional[str] = None
    so_dien_thoai: str
    diem_thuong: float = 0.0
    admin: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    ho_ten: Optional[str] = None
    dia_chi: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    diem_thuong: Optional[float] = None
    admin: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    ngay_tao: datetime
    
    class Config:
        orm_mode = True