from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.thumbnail import Thumbnail
from app.schemas.thumbnail import ThumbnailCreate, ThumbnailUpdate


def get_by_id(db: Session, thumbnail_id: int) -> Optional[Thumbnail]:
    """Lấy thumbnail theo ID"""
    return db.query(Thumbnail).filter(Thumbnail.id == thumbnail_id).first()

def get_by_type_detail_id(db: Session, type_detail_id: int) -> Optional[Thumbnail]:
    """Lấy thumbnail của một sản phẩm cụ thể"""
    return db.query(Thumbnail).filter(Thumbnail.type_detail_id == type_detail_id).first()

def create(db: Session, *, obj_in: ThumbnailCreate) -> Thumbnail:
    """Tạo thumbnail mới"""
    # Kiểm tra xem sản phẩm đã có thumbnail chưa
    existing = get_by_type_detail_id(db, obj_in.type_detail_id)
    if existing:
        # Nếu đã có, cập nhật đường dẫn thay vì tạo mới
        existing.path_to_thumbnail = obj_in.path_to_thumbnail
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Nếu chưa có, tạo mới
    db_obj = Thumbnail(
        type_detail_id=obj_in.type_detail_id,
        path_to_thumbnail=obj_in.path_to_thumbnail
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, *, db_obj: Thumbnail, obj_in: ThumbnailUpdate) -> Thumbnail:
    """Cập nhật thumbnail"""
    update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, *, thumbnail_id: int) -> bool:
    """Xóa thumbnail"""
    thumbnail = get_by_id(db, thumbnail_id)
    if not thumbnail:
        return False
    
    db.delete(thumbnail)
    db.commit()
    return True