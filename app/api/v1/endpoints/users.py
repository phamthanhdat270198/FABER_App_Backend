from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_user import get, is_admin
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import UserBasicInfo

router = APIRouter()


@router.get("/me", response_model=UserBasicInfo)
def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lấy thông tin cơ bản của người dùng hiện tại
    """
    return current_user


@router.get("/{user_id}", response_model=UserBasicInfo)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Lấy thông tin cơ bản của một user cụ thể theo ID
    """
    user = get(db, id=user_id)
    if user == current_user:
        return user
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền truy cập thông tin người dùng khác",
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    return user


@router.get("/", response_model=List[UserBasicInfo])
def read_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Lấy danh sách tất cả người dùng với thông tin cơ bản.
    Chỉ admin mới có quyền truy cập.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.put("/grant-admin", response_model=UserBasicInfo)
def grant_admin_by_phone(
    phone_number: str,  # Truyền vào số điện thoại của người dùng
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Cấp quyền admin cho người dùng dựa trên số điện thoại.
    Chỉ admin mới có quyền cấp quyền admin cho người khác.
    """
    # Kiểm tra xem người dùng có tồn tại trong cơ sở dữ liệu không, tìm qua số điện thoại
    user = db.query(User).filter(User.so_dien_thoai == phone_number).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với số điện thoại này"
        )
    
    # Kiểm tra nếu người yêu cầu cấp quyền không phải là admin
    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không đủ quyền để cấp quyền admin"
        )
    
    # Cập nhật quyền admin cho người dùng
    user.admin = True
    db.commit()  # Lưu thay đổi vào cơ sở dữ liệu
    db.refresh(user)  # Làm mới đối tượng user với các thay đổi đã được lưu
    
    return user