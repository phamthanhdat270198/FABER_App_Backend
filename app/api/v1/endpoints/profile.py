from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import UserProfileUpdate, UserBasicInfo
from app.crud.crud_user import update

router = APIRouter()

@router.get("/me", response_model=UserBasicInfo)
def read_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Lấy thông tin profile của người dùng hiện tại
    """
    return current_user

@router.put("/me", response_model=UserBasicInfo)
def update_user_profile(
    profile_in: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Cập nhật thông tin profile của người dùng hiện tại
    """
    updated_user = update(db, db_obj=current_user, obj_in=profile_in)
    return updated_user