from pydantic import BaseModel
from typing import List, Optional

# === API 1: Schemas cho danh sách loại sơn ===
class PaintTypeItem(BaseModel):
    id: int
    name: str

class PaintTypeListResponse(BaseModel):
    paint_types: List[PaintTypeItem]

# === API 2: Schemas cho danh sách sản phẩm theo loại sơn ===
class ProductItem(BaseModel):
    id: int
    name: str
    volume: Optional[float] = None
    price: Optional[float] = None
    image_path: Optional[str] = None

class ProductListResponse(BaseModel):
    paint_type_id: int
    paint_type_name: str
    products: List[ProductItem]

# === API 3: Schema cho chi tiết sản phẩm ===
class ProductDetailResponse(BaseModel):
    id: int
    product_name: str
    code: Optional[str] = None
    package: Optional[str] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    m2_cover: Optional[float] = None
    promotion: Optional[str] = None
    
    # Thông tin về loại sơn
    paint_type_id: int
    paint_type_name: str
    mo_ta_san_pham: str
    thanh_phan: str
    huong_dan_su_dung: str
    luu_y: Optional[str] = None
    bao_quan: str
    
    # Danh sách đường dẫn ảnh
    images: List[str] = []

class ProductDetailAsVolumeResponse(BaseModel):
    id: int
    product_name: str
    code: Optional[str] = None
    volume: Optional[float] = None
    price: Optional[float] = None

    # Danh sách đường dẫn ảnh
    images: List[str] = []
    thumbnails: List[str] = []

class ProductVariant(BaseModel):
    id: int
    product_name: str
    code: Optional[str] = None
    volume: Optional[float] = None
    package: Optional[str] = None
    price: Optional[float] = None
    m2_cover: Optional[float] = None
    promotion: Optional[str] = None
    images: List[str] = []
    thumbnails: List[str] = []
    is_current: bool = False
    features: str

class VolumeGroup(BaseModel):
    volume: Optional[float] = None
    variants: ProductVariant 

class ProductDetailGroupedResponse(BaseModel):
    id: int
    product_name: str
    code: Optional[str] = None
    paint_type_id: int
    paint_type_name: str
    mo_ta_san_pham: Optional[str] = None
    thanh_phan: Optional[str] = None
    huong_dan_su_dung: Optional[str] = None
    luu_y: Optional[str] = None
    bao_quan: Optional[str] = None
    volume_groups: List[VolumeGroup] = []