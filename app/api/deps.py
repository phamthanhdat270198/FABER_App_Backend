from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User, UserStatus
from app.crud.crud_user import get, is_admin
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.token import TokenPayload

# Endpoint đăng nhập
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không thể xác thực thông tin người dùng",
        )
        
    user = get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Không tìm thấy người dùng"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.status != UserStatus.ACCEPTED and not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đang chờ xác nhận từ admin",
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Người dùng không có quyền admin",
        )
    return current_user