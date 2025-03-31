from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.base import SessionLocal
from app.db.base import get_db
from app.models.type_detail import TypeDetail
from app.models.paint_type import PaintType
from app.models.image_resource import ImageResource
from app.models.thumbnail import Thumbnail
from app.schemas.products import PaintTypeListResponse, PaintTypeItem, ProductListResponse, ProductItem, \
                                ProductDetailResponse, ProductDetailAsVolumeResponse, ProductDetailGroupedResponse      

def get_product_detail(
    product_id, db ):
    """
    API 3: Lấy chi tiết đầy đủ của một sản phẩm và các phiên bản khác trong cùng loại sơn
    """
    # Lấy thông tin sản phẩm
    product = db.query(TypeDetail).filter(TypeDetail.id == product_id).first()
    products = db.query(TypeDetail).filter(TypeDetail.paint_type_id == 1).all()
    print("products ======== ", products)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm"
        )
    
    # Lấy thông tin loại sơn
    paint_type = db.query(PaintType).filter(PaintType.id == product.paint_type_id).first()
    
    # Lấy tất cả sản phẩm thuộc cùng paint_type_id (bao gồm cả sản phẩm hiện tại)
    all_products = db.query(TypeDetail).filter(
        TypeDetail.paint_type_id == product.paint_type_id
    ).all()
    
    print("all product === ", all_products)
    # Tạo danh sách tất cả các phiên bản với thông tin ảnh và thumbnail riêng
    all_variants = []
    
    for prod in all_products:
        # Lấy ảnh của sản phẩm này
        images = db.query(ImageResource).filter(ImageResource.type_detail_id == prod.id).first()
        # image_paths = [img.image_path for img in images]
        # print("len images = ", len(images))
        image_paths = images.image_path
        
        # Lấy thumbnails của sản phẩm này
        thumbnails = db.query(Thumbnail).filter(Thumbnail.type_detail_id == prod.id).first()
        # thumbnail_paths = [thumb.path_to_thumbnail for thumb in thumbnails]
        thumbnail_paths = thumbnails.path_to_thumbnail
        
        all_variants.append({
            "id": prod.id,
            "product_name": prod.product,
            "code": prod.code,
            "volume": prod.volume,
            "package": prod.package,
            "price": prod.price,
            "m2_cover": prod.m2_cover,
            "promotion": prod.promotion,
            "images": image_paths,
            "thumbnails": thumbnail_paths,
            "is_current": (prod.id == product_id),  # Đánh dấu sản phẩm hiện tại
            "features": prod.features
        })
    
    # Nhóm các phiên bản theo volume
    volume_groups = {}
    for variant in all_variants:
        volume = variant.get("volume")
        if volume not in volume_groups:
            volume_groups[volume] = []
        volume_groups[volume] =  variant
    
    # print("volume groups == ", volume_groups)
    # Chuyển đổi dict thành list và sắp xếp theo volume
    grouped_variants = []
    for volume, variants in sorted(volume_groups.items(), key=lambda x: x[0] if x[0] is not None else 0):
        grouped_variants.append({
            "volume": volume,
            "variants": variants
        })
    
    # Tạo response
    return {
        "id": product.id,
        "product_name": product.product,
        "code": product.code,
        "paint_type_id": paint_type.id,
        "paint_type_name": paint_type.paint_type,
        # Thông tin chung
        "mo_ta_san_pham": paint_type.mo_ta_san_pham,
        "thanh_phan": paint_type.thanh_phan,
        "huong_dan_su_dung": paint_type.huong_dan_su_dung,
        "luu_y": paint_type.luu_y,
        "bao_quan": paint_type.bao_quan,
        # Các phiên bản được nhóm theo volume
        "volume_groups": grouped_variants
    }

def get_products_by_paint_type(
    paint_type_id,
    preferred_volume,
    db
):
    """
    API 2: Lấy danh sách sản phẩm theo loại sơn
    
    Ưu tiên lấy sản phẩm có volume chỉ định (mặc định là 5), 
    nếu không có sẽ lấy volume hiện có của sản phẩm
    """
    # Kiểm tra loại sơn có tồn tại không
    paint_type = db.query(PaintType).filter(PaintType.id == paint_type_id).first()
    if not paint_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sơn"
        )
    
    # Lấy tất cả sản phẩm thuộc loại sơn
    all_products = db.query(TypeDetail).filter(TypeDetail.paint_type_id == paint_type_id).all()
    
    # Nhóm sản phẩm theo tên để xử lý volume
    product_groups = {}
    for product in all_products:
        if product.product not in product_groups:
            product_groups[product.product] = []
        product_groups[product.product].append(product)
    
    result = []
    for product_name, products in product_groups.items():
        # Tìm sản phẩm có volume ưu tiên (mặc định là 5)
        preferred_product = next((p for p in products if p.volume == preferred_volume), None)
        
        # Nếu không có sản phẩm ưu tiên, lấy sản phẩm đầu tiên
        selected_product = preferred_product if preferred_product else products[0]
        
        # Lấy ảnh đầu tiên của sản phẩm nếu có
        image = db.query(ImageResource).filter(ImageResource.type_detail_id == selected_product.id).first()
        image_path = image.image_path if image else None
        
        result.append(ProductItem(
            id=selected_product.id,
            name=selected_product.product,
            volume=selected_product.volume,
            price=selected_product.price,
            image_path=image_path
        ))
    
    return {
        "paint_type_id": paint_type_id,
        "paint_type_name": paint_type.paint_type,
        "products": result
    }

if __name__ == "__main__":
    db = SessionLocal()
    # out = get_product_detail(1, db)
    out = get_products_by_paint_type(1, 5, db)
    print("out == ", out)