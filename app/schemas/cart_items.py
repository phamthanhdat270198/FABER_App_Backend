from pydantic import BaseModel

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

    class Config:
        orm_mode = True