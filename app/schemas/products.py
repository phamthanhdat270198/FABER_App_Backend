from pydantic import BaseModel
from typing import List, Optional
from app.schemas.image_resource import ImageResourceResponse

class PaintTypeInfo(BaseModel):
    id: int
    paint_type: str
    mo_ta_san_pham: str
    thanh_phan: str
    huong_dan_su_dung: str
    luu_y: Optional[str] = None
    bao_quan: str
    
    class Config:
        orm_mode = True

class ProductDetail(BaseModel):
    id: int
    paint_type_id: int
    product: str
    code: Optional[str] = None
    package: Optional[str] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    m2_cover: Optional[float] = None
    promotion: Optional[str] = None
    
    # Thông tin về loại sơn
    paint_type: PaintTypeInfo
    
    # Danh sách ảnh sản phẩm
    images: List[ImageResourceResponse] = []
    
    class Config:
        orm_mode = True

class ProductListResponse(BaseModel):
    total: int
    products: List[ProductDetail]