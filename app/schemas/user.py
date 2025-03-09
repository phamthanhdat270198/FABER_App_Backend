from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, date
from enum import Enum

class UserStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"

class UserGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class UserBase(BaseModel):
    ho_ten: str
    dia_chi: Optional[str] = None
    so_dien_thoai: str
    diem_thuong: float = 0.0
    admin: bool = False
    status: UserStatusEnum = UserStatusEnum.PENDING
    date_of_birth: Optional[date] = None
    gender: Optional[UserGender] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    ho_ten: Optional[str] = None
    dia_chi: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    diem_thuong: Optional[float] = None
    password: Optional[str] = None
    status: Optional[UserStatusEnum] = None
    date_of_birth: Optional[date] = None
    gender: Optional[UserGender] = None
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is not None:
            # Kiểm tra người dùng phải lớn hơn 10 tuổi
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 10:
                raise ValueError('Người dùng phải lớn hơn 10 tuổi')
        return v

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
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    
    class Config:
        orm_mode = True

# Schema cho cập nhật profile
class UserProfileUpdate(BaseModel):
    ho_ten: Optional[str] = None
    dia_chi: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[UserGender] = None
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is not None:
            # Kiểm tra người dùng phải lớn hơn 10 tuổi
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError('Người dùng phải lớn hơn 18 tuổi')
        return v
    
    class Config:
        orm_mode = True