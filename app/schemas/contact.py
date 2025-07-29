# app/schemas/contact.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class ContactInquiryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tên khách hàng")
    phone_number: str = Field(..., min_length=8, max_length=15, description="Số điện thoại khách hàng")
    product_of_interest: str = Field(..., min_length=1, max_length=100, description="Sản phẩm quan tâm")
    message: Optional[str] = Field(None, max_length=500, description="Lời nhắn từ khách hàng")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        cleaned = v.replace('+', '').replace('-', '').replace(' ', '')
        if not cleaned.isdigit():
            raise ValueError('Số điện thoại chỉ được chứa chữ số, +, -, hoặc khoảng trắng')
        return v

class ContactInquiryCreate(ContactInquiryBase):
    pass

class ContactInquiryUpdate(ContactInquiryBase):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    product_of_interest: Optional[str] = None
    message: Optional[str] = None

class ContactInquiryInDBBase(ContactInquiryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ContactInquiry(ContactInquiryInDBBase):
    pass

class ContactInquiryDetail(ContactInquiryInDBBase):
    pass