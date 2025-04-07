from pydantic import BaseModel
from typing import List

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