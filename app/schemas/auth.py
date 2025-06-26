from typing import Optional

from pydantic import BaseModel, Field


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