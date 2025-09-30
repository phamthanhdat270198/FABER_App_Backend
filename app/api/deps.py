from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models.user import User, UserStatus
from app.crud.crud_user import get, is_admin
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas.token import TokenPayload
from fastapi.security import HTTPBearer
security = HTTPBearer(auto_error=False)

# Endpoint đăng nhập
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/json")


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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc đã bị xóa",
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

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(security)
) -> Optional[User]:
    """
    Dependency để lấy user hiện tại, trả về None nếu không có token hoặc token không hợp lệ
    Không raise exception, cho phép anonymous access
    """
    if not token:
        return None
    
    try:
        # Extract token từ HTTPAuthorizationCredentials nếu có
        token_str = token.credentials if hasattr(token, 'credentials') else token
        
        # Decode JWT token
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
            
    except JWTError:
        # Token không hợp lệ, trả về None thay vì raise exception
        return None
    
    # Tìm user trong database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        return None
        
    # Kiểm tra user có active không
    if not user.is_active:
        return None
        
    return user