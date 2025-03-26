# app/api/routes/contacts.py
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import crud_contact
from app.models.contact import ContactInquiry
from app.schemas.contact import (
    ContactInquiry as ContactInquirySchema,
    ContactInquiryCreate,
    ContactInquiryUpdate,
    ContactInquiryDetail
)

router = APIRouter()


@router.post("/", response_model=ContactInquirySchema, status_code=status.HTTP_201_CREATED)
def create_contact(
    *,
    db: Session = Depends(get_db),
    contact_in: ContactInquiryCreate,
) -> Any:
    """
    Tạo mới một liên hệ mua hàng
    """
    contact = crud_contact.create(db=db, obj_in=contact_in)
    return contact


@router.get("/", response_model=List[ContactInquirySchema])
def read_contacts(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Lấy danh sách tất cả liên hệ mua hàng
    """
    contacts = crud_contact.get_multi(db=db, skip=skip, limit=limit)
    return contacts


@router.get("/{contact_id}", response_model=ContactInquiryDetail)
def read_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: int,
) -> Any:
    """
    Lấy thông tin chi tiết một liên hệ mua hàng theo ID
    """
    contact = crud_contact.get(db=db, id=contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy liên hệ mua hàng"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactInquirySchema)
def update_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: int,
    contact_in: ContactInquiryUpdate,
) -> Any:
    """
    Cập nhật thông tin một liên hệ mua hàng
    """
    contact = crud_contact.get(db=db, id=contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy liên hệ mua hàng"
        )
    contact = crud_contact.update(db=db, db_obj=contact, obj_in=contact_in)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    *,
    db: Session = Depends(get_db),
    contact_id: int,
) -> None:
    """
    Xóa một liên hệ mua hàng
    """
    contact = crud_contact.get(db=db, id=contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy liên hệ mua hàng"
        )
    crud_contact.delete(db=db, id=contact_id)
