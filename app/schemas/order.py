from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

# Enum cho trạng thái đơn hàng trong Pydantic schema
class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    ACCEPT = "accept"

# Schema cơ bản cho Order
class OrderBase(BaseModel):
    user_id: int
    status: OrderStatusEnum = OrderStatusEnum.PENDING

# Schema cho tạo Order mới
class OrderCreate(OrderBase):
    pass

# Schema cho cập nhật Order
class OrderUpdate(BaseModel):
    status: Optional[OrderStatusEnum] = None
    is_deleted: Optional[bool] = None

# Schema cho phản hồi Order
class OrderResponse(OrderBase):
    id: int
    date_time: datetime
    is_deleted: bool

    class Config:
        orm_mode = True

# Schema cho hiển thị Order với thông tin User
class OrderWithUser(OrderResponse):
    user_ho_ten: str

    class Config:
        orm_mode = True