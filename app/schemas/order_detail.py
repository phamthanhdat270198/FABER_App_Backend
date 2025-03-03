from pydantic import BaseModel, Field
from typing import Optional

class OrderDetailBase(BaseModel):
    order_id: int
    type_detail_id: int
    quantity: int = Field(default=1, gt=0)
    total_amount: float = Field(gt=0)

class OrderDetailCreate(OrderDetailBase):
    pass

class OrderDetailUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    total_amount: Optional[float] = Field(None, gt=0)

class OrderDetailResponse(OrderDetailBase):
    id: int
    
    class Config:
        orm_mode = True

class OrderDetailWithProduct(OrderDetailResponse):
    product_name: str
    product_code: Optional[str] = None
    unit_price: Optional[float] = None
    
    class Config:
        orm_mode = True