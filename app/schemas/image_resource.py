from pydantic import BaseModel, Field
from typing import Optional, List

class ImageResourceBase(BaseModel):
    image_path: str
    type_detail_id: int

class ImageResourceCreate(ImageResourceBase):
    pass

class ImageResourceUpdate(BaseModel):
    image_path: Optional[str] = None
    type_detail_id: Optional[int] = None

class ImageResourceResponse(ImageResourceBase):
    id: int
    
    class Config:
        orm_mode = True

# Schema để trả về danh sách ảnh cho một sản phẩm
class ProductImagesResponse(BaseModel):
    product_id: int
    product_name: str
    images: List[ImageResourceResponse]
    
    class Config:
        orm_mode = True