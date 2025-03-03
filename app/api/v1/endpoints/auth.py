from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# from app import crud
from app.crud.crud_user import authenticate, get_by_phone, create
from app.api.deps import get_db
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.token import Token
from app.schemas.auth import Login, UserAuth
from app.schemas.user import UserResponse, UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, lấy access token cho future requests
    Sử dụng số điện thoại như username
    """
    # user = crud.crud_user.authenticate(
    #     db, so_dien_thoai=form_data.username, password=form_data.password
    # )
    user = authenticate(
        db, so_dien_thoai=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/json", response_model=Token)
def login_access_token_json(
    login_data: Login,
    db: Session = Depends(get_db)
) -> Any:
    """
    JSON format login, thuận tiện cho frontend
    """
    # user = crud.crud_user.authenticate(
    #     db, so_dien_thoai=login_data.so_dien_thoai, password=login_data.password
    # )
    user = authenticate(
        db, so_dien_thoai=login_data.so_dien_thoai, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại hoặc mật khẩu không chính xác",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserAuth,
) -> Any:
    """
    Đăng ký tài khoản người dùng mới
    """
    # user = crud.crud_user.get_by_phone(db, so_dien_thoai=user_in.so_dien_thoai)
    user = get_by_phone(db, so_dien_thoai=user_in.so_dien_thoai)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại này đã được đăng ký",
        )
    
    user_data = user_in.dict()
    user_create = UserCreate(
        **user_data,
        admin=False,  # Người dùng mới không có quyền admin
    )
    # user = crud.crud_user.create(db, obj_in=user_create)
    user = create(db, obj_in=user_create)

    return user