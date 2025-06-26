from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: int
    color_code: str
    volume: float
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    color_code: str
    volume: float
    quantity: int
    product: str
    price: float

    class Config:
        orm_mode = True

class CartItemThumbnailResponse(BaseModel):
    id: int
    product_id: int
    color_code: str
    volume: float
    quantity: int
    product: str
    price: float
    thumbnail: str
    reward: int
    code: str

    class Config:
        orm_mode = True
class DeleteIDCart(BaseModel):
    delete_ids: List[int]

class OrderCreate(BaseModel):
    cart_item_ids: List[int]

class OrderResponse(BaseModel):
    message: str
    items_count: int
    total_amount: float
    reward_points_earned: float
    total_reward_points: float
    
    class Config:
        orm_mode = True

# class HistoryResponse(BaseModel):
class UnpaidOrderItemResponse(BaseModel):
    id: int
    product: str            
    code: str               
    volume: float            
    color_code: str          
    quantity: int            
    order_date: datetime     
    total_price: float     
    image_path: str          

    class Config:
        orm_mode = True
    # from_attributes = True #new version of orm mode

class paidOrderItemResponse(BaseModel):
    id: int
    product: str            
    code: str               
    volume: float            
    color_code: str          
    quantity: int            
    order_date: datetime     
    total_price: float     
    image_path: str    
    bonus_points: float      

    class Config:
        orm_mode = True
class UnpaidOrderHistoryResponse(BaseModel):
    message: str
    total_items: int
    total_amount: float
    orders: List[UnpaidOrderItemResponse]

class PaidOrderHistoryResponse(BaseModel):
    message: str
    total_items: int
    total_amount: float
    orders: List[paidOrderItemResponse]

class UnpaidOrderItemForAdmin(BaseModel):
    """Item chưa thanh toán trong group user"""
    cart_item_id: int
    product: str
    code: str
    volume: float
    color_code: str
    quantity: int
    unit_price: float
    total_price: float
    order_date: datetime
    days_pending: int
    image_path: Optional[str] = None

class UserUnpaidGroup(BaseModel):
    """Group unpaid orders theo user"""
    user_id: int
    user_name: str
    user_phone: str
    user_address: Optional[str] = None
    is_retail_customer: bool
    is_agent: bool
    total_unpaid_items: int
    total_unpaid_amount: float
    unpaid_orders: List[UnpaidOrderItemForAdmin]

class AdminGroupedUnpaidResponse(BaseModel):
    """Response group theo user"""
    message: str
    total_users_with_unpaid: int
    total_unpaid_items: int
    total_unpaid_amount: float
    users: List[UserUnpaidGroup]


class UpdateCartItemRequest(BaseModel):
    cart_item_id: int
    product_name: Optional[str] = None      # Tên sản phẩm mới
    quantity: Optional[int] = Field(None, ge=1)  # Số lượng (>= 1)
    color_code: Optional[str] = None        # Mã màu mới
    volume: Optional[float] = Field(None, gt=0)  # Kích thước mới (> 0)

class BatchUpdateRequest(BaseModel):
    user_id: int  # ID của user sở hữu đơn hàng
    updates: List[UpdateCartItemRequest]

# class UpdatedItemResponse(BaseModel):
#     cart_item_id: int
#     old_product: str
#     new_product: str
#     old_quantity: int
#     new_quantity: int
#     old_color_code: str
#     new_color_code: str
#     old_volume: float
#     new_volume: float
#     old_bonus_points: int
#     new_bonus_points: int
#     price_change: float

# class AdminUpdateResponse(BaseModel):
#     message: str
#     updated_items: List[UpdatedItemResponse]
#     total_items_updated: int
#     old_total_bonus_points: int
#     new_total_bonus_points: int
#     bonus_points_difference: int