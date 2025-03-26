from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.contact import ContactInquiry
from app.schemas.contact import ContactInquiryCreate, ContactInquiryUpdate

def create(db: Session, *, obj_in: ContactInquiryCreate) -> ContactInquiry:
    """
    Tạo mới một liên hệ mua hàng
    """
    db_obj = ContactInquiry(
        name=obj_in.name,
        phone_number=obj_in.phone_number,
        product_of_interest=obj_in.product_of_interest,
        message=obj_in.message
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get(db: Session, *, id: int) -> Optional[ContactInquiry]:
    """
    Lấy thông tin một liên hệ mua hàng theo ID
    """
    return db.query(ContactInquiry).filter(ContactInquiry.id == id).first()

def get_multi(db: Session, *, skip: int = 0, limit: int = 100) -> List[ContactInquiry]:
    """
    Lấy danh sách nhiều liên hệ mua hàng với phân trang
    """
    return db.query(ContactInquiry).offset(skip).limit(limit).all()

def update(
    db: Session, *, db_obj: ContactInquiry, obj_in: ContactInquiryUpdate
) -> ContactInquiry:
    """
    Cập nhật thông tin liên hệ mua hàng
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, *, id: int) -> Optional[ContactInquiry]:
    """
    Xóa một liên hệ mua hàng
    """
    obj = db.query(ContactInquiry).get(id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj