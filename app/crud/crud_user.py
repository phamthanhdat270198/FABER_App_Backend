from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_by_phone(db: Session, so_dien_thoai: str) -> Optional[User]:
    return db.query(User).filter(User.so_dien_thoai == so_dien_thoai).first()


def get(db: Session, id: int) -> Optional[User]:
    return db.query(User).filter(User.id == id).first()


def create(db: Session, *, obj_in: UserCreate) -> User:
    db_obj = User(
        ho_ten=obj_in.ho_ten,
        dia_chi=obj_in.dia_chi,
        so_dien_thoai=obj_in.so_dien_thoai,
        diem_thuong=obj_in.diem_thuong,
        admin=obj_in.admin,
        hashed_password=get_password_hash(obj_in.password)
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate(db: Session, *, so_dien_thoai: str, password: str) -> Optional[User]:
    user = get_by_phone(db=db, so_dien_thoai=so_dien_thoai)
    if not user:
        return None
    if not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_admin(user: User) -> bool:
    return user.admin