from datetime import timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.crud_user import authenticate, get_by_phone, create, is_admin, get, update
from app.api.deps import get_db
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.token import Token
from app.schemas.auth import Login, UserAuth
from app.schemas.user import UserResponse, UserCreate, UserBasicInfo, UserUpdate, UserStatusEnum, UserStatusInfo
from app.models.user import User, UserStatus
from fastapi import Cookie, Header
from app.crud import crud_token_store

router = APIRouter()



@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, lấy access token cho future requests
    Sử dụng số điện thoại như username
    """
    user = authenticate(
        db, so_dien_thoai=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kiểm tra xem tài khoản đã được chấp nhận chưa
    if user.status != UserStatus.ACCEPTED and not user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đang chờ xác nhận từ admin",
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
    user = authenticate(
        db, so_dien_thoai=login_data.so_dien_thoai, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại hoặc mật khẩu không chính xác",
        )
    
    # Kiểm tra xem tài khoản đã được chấp nhận chưa
    if user.status != UserStatus.ACCEPTED and not user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đang chờ xác nhận từ admin",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register-request", status_code=status.HTTP_201_CREATED)
def create_registration_request(
    *,
    db: Session = Depends(get_db),
    user_in: UserAuth
) -> Any:
    """
    Tạo yêu cầu đăng ký người dùng mới
    """
    user = get_by_phone(db, so_dien_thoai=user_in.so_dien_thoai)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại này đã được đăng ký",
        )
    
    # Tạo người dùng mới với trạng thái PENDING
    user_data = user_in.dict()
    user_create = UserCreate(
        **user_data,
        admin=False,  # Người dùng mới không có quyền admin
        status=UserStatusEnum.PENDING  # Mặc định là đang chờ xác nhận
    )
    user = create(db, obj_in=user_create)
    
    return {"message": "Đã tạo yêu cầu đăng ký thành công, chờ admin xác nhận"}


@router.get("/pending-registrations", response_model=List[UserStatusInfo])
def get_pending_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Lấy danh sách yêu cầu đăng ký đang chờ xác nhận
    Chỉ admin mới có quyền truy cập
    """
    pending_users = (
        db.query(User)
        .filter(User.status == UserStatus.PENDING)
        .order_by(User.ngay_tao.desc())
        .all()
    )
    return pending_users

@router.get("/accepted-registrations", response_model=List[UserStatusInfo])
def get_pending_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Lấy danh sách yêu cầu đăng ký đang chờ xác nhận
    Chỉ admin mới có quyền truy cập
    """
    accepted_users = (
        db.query(User)
        .filter(User.status == UserStatus.ACCEPTED)
        .order_by(User.ngay_tao.desc())
        .all()
    )
    
    return accepted_users


@router.post("/approve-registration/{user_id}", response_model=UserBasicInfo)
def approve_registration(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Phê duyệt yêu cầu đăng ký
    Chỉ admin mới có quyền thực hiện
    """
    user = get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng",
        )
    
    if user.status == UserStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng này đã được phê duyệt trước đó",
        )
    
    # Cập nhật trạng thái thành ACCEPTED
    user_update = UserUpdate(status=UserStatusEnum.ACCEPTED)
    updated_user = update(db, db_obj=user, obj_in=user_update)
    
    return updated_user

@router.post("/login/remember", response_model=Token)
def login_remember_me(
    login_data: Login,
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Any:
    """
    Đăng nhập với tính năng Remember Me
    Tạo token ngắn hạn (JWT) và token dài hạn (lưu trong database)
    """
    user = authenticate(
        db, so_dien_thoai=login_data.so_dien_thoai, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Số điện thoại hoặc mật khẩu không chính xác",
        )
    
    # Kiểm tra xem tài khoản đã được chấp nhận chưa
    if user.status != UserStatus.ACCEPTED and not user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản đang chờ xác nhận từ admin",
        )
    
    # Tạo access token JWT bình thường
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    # Tạo remember token dài hạn (30 ngày)
    remember_token = crud_token_store.create_token(
        db=db, 
        user_id=user.id, 
        expires_days=30,
        device_info=user_agent
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "remember_token": remember_token.token
    }


@router.post("/refresh-token")
def refresh_token(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Làm mới access token sử dụng remember token
    """
    # Tìm token trong database
    db_token = crud_token_store.get_by_token(db, token)
    
    if not db_token or not db_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn",
        )
    
    # Cập nhật thời gian sử dụng gần nhất
    db_token = crud_token_store.update_last_used(db, db_token)
    
    # Tạo access token JWT mới
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        db_token.user_id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Đăng xuất bằng cách thu hồi remember token
    """
    success = crud_token_store.revoke_token(db, token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token không hợp lệ",
        )
    
    return {"message": "Đăng xuất thành công"}


@router.post("/logout-all-devices")
def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Đăng xuất khỏi tất cả thiết bị bằng cách thu hồi tất cả token
    """
    count = crud_token_store.revoke_all_tokens_for_user(db, current_user.id)
    
    return {
        "message": f"Đã đăng xuất khỏi {count} thiết bị",
        "count": count
    }