from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class UserStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"

class UserBase(BaseModel):
    ho_ten: str
    dia_chi: Optional[str] = None
    so_dien_thoai: str
    diem_thuong: float = 0.0
    admin: bool = False
    status: UserStatusEnum = UserStatusEnum.PENDING

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    ho_ten: Optional[str] = None
    dia_chi: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    diem_thuong: Optional[float] = None
    password: Optional[str] = None
    status: Optional[UserStatusEnum] = None

class UserResponse(UserBase):
    id: int
    ngay_tao: datetime
    
    class Config:
        orm_mode = True

# Schema chỉ chứa thông tin cơ bản cho API
class UserBasicInfo(BaseModel):
    id: int
    ho_ten: str
    dia_chi: Optional[str] = None
    so_dien_thoai: str
    admin: bool
    status: UserStatusEnum
    
    class Config:
        orm_mode = True