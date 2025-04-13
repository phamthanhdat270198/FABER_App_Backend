from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
# from app.models.rewards_info import  RewardType

class UserStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"

class UserGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class RewardType(str, Enum):
    REGULAR = "REGULAR"
    SPECIAL = "SPECIAL"
    IGNORE = "IGNORE"

class UserBase(BaseModel):
    ho_ten: str
    dia_chi: Optional[str] = None
    so_dien_thoai: str
    diem_thuong: float = 0.0
    admin: bool = False
    status: UserStatusEnum = UserStatusEnum.PENDING
    date_of_birth: Optional[date] = None
    gender: Optional[UserGender] = None
    ngay_tao: datetime

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
    diem_thuong: float
    
    class Config:
        orm_mode = True

class UserStatusInfo(BaseModel):
    id: int
    ho_ten: str
    so_dien_thoai: str
    status: UserStatusEnum
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
            # Kiểm tra người dùng phải lớn hơn 18 tuổi
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError('Người dùng phải lớn hơn 18 tuổi')
        return v
    
    class Config:
        orm_mode = True

class SpinInfoResponse(BaseModel):
    id: int
    nums_spin: int
    kth_spin: int

    class Config:
        orm_mode = True

class UseSpinResponse(BaseModel):
    success: bool
    new_kth_spin: int
    remaining_spins: int
    message: str
    reward_type: str
    reward_img: Optional[str]

class RewardBase(BaseModel):
    name: str
    type: RewardType

    class Config:
        orm_mode = True

class RewardList(BaseModel):
    regular_rewards: List[RewardBase]
    special_rewards: List[RewardBase]
    ignore_rewards:List[RewardBase]
    total_count: int

class SpinRewardBase(BaseModel):
    id: int
    user_id: int
    reward_type: str
    is_claimed: bool
    spin_number: int
    created_at: datetime
    claimed_at: Optional[datetime] = None

    class Config:
        orm_mode = True