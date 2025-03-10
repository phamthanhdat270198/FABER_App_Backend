from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.base import get_db
from app.models.type_detail import TypeDetail
from app.models.paint_type import PaintType
from app.models.image_resource import ImageResource
from app.schemas.products import ProductDetail, ProductListResponse

router = APIRouter()

@router.get("", response_model=ProductListResponse)
def get_all_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
    paint_type_id: Optional[int] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False
):
    """
    Lấy danh sách sản phẩm với đầy đủ thông tin
    
    - **skip**: Số lượng bản ghi bỏ qua (phân trang)
    - **limit**: Số lượng bản ghi tối đa trả về
    - **paint_type_id**: Lọc theo loại sơn
    - **search**: Tìm kiếm theo tên sản phẩm hoặc mã
    - **min_price**: Giá tối thiểu
    - **max_price**: Giá tối đa
    - **sort_by**: Sắp xếp theo trường (product, price, volume)
    - **sort_desc**: Sắp xếp giảm dần (true) hoặc tăng dần (false)
    """
    # Tạo query cơ bản
    query = db.query(TypeDetail)
    
    # Thêm các điều kiện lọc
    if paint_type_id:
        query = query.filter(TypeDetail.paint_type_id == paint_type_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (TypeDetail.product.ilike(search_term)) | 
            (TypeDetail.code.ilike(search_term))
        )
    
    if min_price is not None:
        query = query.filter(TypeDetail.price >= min_price)
    
    if max_price is not None:
        query = query.filter(TypeDetail.price <= max_price)
    
    # Đếm tổng số bản ghi thỏa mãn điều kiện (trước khi phân trang)
    total_count = query.count()
    
    # Sắp xếp
    if sort_by:
        if sort_by == "product":
            order_column = TypeDetail.product
        elif sort_by == "price":
            order_column = TypeDetail.price
        elif sort_by == "volume":
            order_column = TypeDetail.volume
        else:
            order_column = TypeDetail.id
            
        if sort_desc:
            order_column = order_column.desc()
        
        query = query.order_by(order_column)
    else:
        # Mặc định sắp xếp theo ID
        query = query.order_by(TypeDetail.id)
    
    # Phân trang
    products = query.offset(skip).limit(limit).all()
    
    # Lấy thông tin loại sơn và ảnh cho mỗi sản phẩm
    result_products = []
    for product in products:
        # Đã có sẵn relationship để lấy paint_type và images
        result_products.append(product)
    
    return {
        "total": total_count,
        "products": result_products
    }

@router.get("/{product_id}", response_model=ProductDetail)
def get_product_by_id(
    product_id: int = Path(..., title="ID của sản phẩm", ge=1),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin chi tiết của một sản phẩm theo ID
    """
    product = db.query(TypeDetail).filter(TypeDetail.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm"
        )
    
    return product

@router.get("/paint-type/{paint_type_id}", response_model=List[ProductDetail])
def get_products_by_paint_type(
    paint_type_id: int = Path(..., title="ID của loại sơn", ge=1),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    Lấy danh sách sản phẩm theo loại sơn
    """
    # Kiểm tra loại sơn có tồn tại không
    paint_type = db.query(PaintType).filter(PaintType.id == paint_type_id).first()
    if not paint_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sơn"
        )
    
    # Lấy các sản phẩm thuộc loại sơn
    products = db.query(TypeDetail).filter(
        TypeDetail.paint_type_id == paint_type_id
    ).offset(skip).limit(limit).all()
    
    return products

@router.get("/search/{keyword}", response_model=List[ProductDetail])
def search_products(
    keyword: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """
    Tìm kiếm sản phẩm theo từ khóa
    """
    search_term = f"%{keyword}%"
    
    products = db.query(TypeDetail).filter(
        (TypeDetail.product.ilike(search_term)) | 
        (TypeDetail.code.ilike(search_term))
    ).offset(skip).limit(limit).all()
    
    return products