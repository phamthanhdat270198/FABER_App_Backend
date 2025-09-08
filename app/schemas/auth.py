from typing import Optional

from pydantic import BaseModel, Field, validator
import re

class Login(BaseModel):
    so_dien_thoai: str
    password: str


class UserAuth(BaseModel):
    so_dien_thoai: str
    password: str
    ho_ten: str
    dia_chi: Optional[str] = None

class UserAuthWithRole(BaseModel):
    so_dien_thoai: str
    password: str
    ho_ten: str
    dia_chi: Optional[str] = None
    is_retail_customer: bool
    is_agent: bool

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

    @validator('ho_ten')
    def validate_name(cls, v):
        if v is not None:
            # Loại bỏ khoảng trắng đầu cuối
            name_clean = v.strip()
            
            # Kiểm tra không được rỗng sau khi trim
            if not name_clean:
                raise ValueError('Họ tên không được để trống')
            
            # Kiểm tra độ dài
            if len(name_clean) < 2:
                raise ValueError('Họ tên phải có ít nhất 2 ký tự')
            
            if len(name_clean) > 100:
                raise ValueError('Họ tên không được quá 100 ký tự')
            
            # Kiểm tra chỉ chứa chữ cái, khoảng trắng và một số ký tự đặc biệt của tiếng Việt
            if not re.match(r'^[a-zA-ZÀ-ỹ\s\-\.]+$', name_clean):
                raise ValueError('Họ tên chỉ được chứa chữ cái, khoảng trắng, dấu gạch ngang và dấu chấm')
            
            return name_clean
        return v