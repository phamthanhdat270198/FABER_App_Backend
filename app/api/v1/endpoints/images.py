from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.type_detail import TypeDetail
from app.models.image_resource import ImageResource
from app.schemas.image_resource import ImageResourceResponse, ProductImagesResponse

router = APIRouter()

@router.get("/product/{product_id}", response_model=ProductImagesResponse)
def get_product_images(
    product_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy tất cả ảnh của một sản phẩm cụ thể
    """
    product = db.query(TypeDetail).filter(TypeDetail.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm"
        )
    
    images = db.query(ImageResource).filter(ImageResource.type_detail_id == product_id).all()
    
    return {
        "product_id": product.id,
        "product_name": product.product,
        "images": images
    }

@router.get("/products", response_model=List[ProductImagesResponse])
def get_all_products_with_images(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Lấy tất cả sản phẩm kèm theo ảnh của chúng
    """
    products = db.query(TypeDetail).offset(skip).limit(limit).all()
    
    result = []
    for product in products:
        images = db.query(ImageResource).filter(ImageResource.type_detail_id == product.id).all()
        result.append({
            "product_id": product.id,
            "product_name": product.product,
            "images": images
        })
    
    return result