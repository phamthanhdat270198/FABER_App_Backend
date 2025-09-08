from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta, date
from enum import Enum
import re
# from app.models.rewards_info import  RewardType
# def get_date_time():
#     utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
#     # Chuyển sang giờ Việt Nam (UTC+7)
#     vn_time = utc_now.astimezone(timezone(timedelta(hours=7)))
#     return vn_time
class UserStatusEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINE = "DECLINE"

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

#for new register

class UserBaseRegister(BaseModel):
    ho_ten: str
    dia_chi: Optional[str] = None
    so_dien_thoai: str
    diem_thuong: float = 0.0
    admin: bool = False
    status: UserStatusEnum = UserStatusEnum.PENDING
    date_of_birth: Optional[date] = None
    gender: Optional[UserGender] = None
    ngay_tao: datetime = Field(
        default_factory=lambda: datetime.now(timezone(timedelta(hours=7)))
    )
    is_agent: bool = False
    is_retail_customer: bool = False
    user_code: Optional[str] = None  # Mã người dùng


class UserCreateRegister(UserBaseRegister):
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
    user_code: Optional[str] = None  # Mã người dùng
    
    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        if v is not None:
            # Kiểm tra người dùng phải lớn hơn 10 tuổi
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 10:
                raise ValueError('Người dùng phải lớn hơn 10 tuổi')
        return v
    
    @validator('so_dien_thoai')
    def validate_phone_number(cls, v):
        if v is not None:
            # Loại bỏ khoảng trắng và ký tự đặc biệt
            phone_clean = re.sub(r'\s+|-|\.|\(|\)', '', v)
            
            # Kiểm tra chỉ chứa số
            if not phone_clean.isdigit():
                raise ValueError('Số điện thoại chỉ được chứa chữ số')
            
            # Kiểm tra độ dài = 10
            if len(phone_clean) != 10:
                raise ValueError('Số điện thoại phải có độ dài 10 chữ số')
            
            # Kiểm tra bắt đầu bằng số 0
            if not phone_clean.startswith('0'):
                raise ValueError('Số điện thoại phải bắt đầu bằng số 0')
            
            # Kiểm tra số thứ hai hợp lệ (theo chuẩn Việt Nam)
            valid_second_digits = ['3', '5', '7', '8', '9']  # 03x, 05x, 07x, 08x, 09x
            if phone_clean[1] not in valid_second_digits:
                raise ValueError('Số điện thoại không đúng định dạng Việt Nam (phải là 03x, 05x, 07x, 08x, 09x)')
            
            return phone_clean  # Trả về số đã được làm sạch
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
    ngay_tao: datetime
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
    id: int
    success: bool
    new_kth_spin: int
    remaining_spins: int
    message: str
    reward_type: str
    reward_img: Optional[str]

class RewardBase(BaseModel):
    id: int
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
    reward_img_url: str

    class Config:
        orm_mode = True