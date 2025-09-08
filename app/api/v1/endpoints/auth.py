from datetime import timedelta
from typing import Any, List, Optional
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.crud_user import authenticate, get_by_phone, create, is_admin, get, update
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.api.third_party_func import add_customer_to_kiot, get_kiot_token, get_branch_id
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.schemas.token import Token
from app.schemas.auth import Login, UserAuth, UserAuthWithRole
from app.schemas.user import UserResponse, UserCreate, UserCreateRegister, UserBasicInfo, UserUpdate, UserStatusEnum, UserStatusInfo
from app.models.user import User, UserStatus
from fastapi import Cookie, Header
from app.crud import crud_token_store

router = APIRouter()

def get_date_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Chuyển sang giờ Việt Nam (UTC+7)
    vn_time = utc_now.astimezone(timezone(timedelta(hours=7)))
    return vn_time

@router.post("/login", response_model=Token)
def login_access_token(
    login_data: Login,
    db: Session = Depends(get_db)
) -> Any:
    """
    Đăng nhập và trả về access token + refresh token
    Hỗ trợ tính năng remember me
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
    
    # Tạo access token JWT (ngắn hạn)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    refresh_token = crud_token_store.create_token_no_remember(
        db=db, 
        user_id=user.id, 
        expires_days=REFRESH_TOKEN_EXPIRE_DAYS,
    )
    
    # Trả về cả access token và refresh token
    token_response = {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token.token,
        "expires_at": refresh_token.expires_at
    }
    
    return token_response

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
        status=UserStatusEnum.PENDING,  # Mặc định là đang chờ xác nhận
        ngay_tao=get_date_time()
    )
    user = create(db, obj_in=user_create)
    
    return {"message": "Đã tạo yêu cầu đăng ký thành công, chờ admin xác nhận"}


@router.post("/register-request-specific", status_code=status.HTTP_201_CREATED)
def create_registration_request_specific(
    *,
    db: Session = Depends(get_db),
    user_in: UserAuthWithRole
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
    
    if not user_in.is_retail_customer and not user_in.is_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User phải thuộc ít nhất một loại: khách lẻ hoặc đại lý",
        )

    # Tạo mã khách hàng tự động
    def generate_user_code(db: Session) -> str:
        """
        Tạo mã khách hàng theo format KH000, KH001, ... với độ dài tự động mở rộng
        """
        prefix = "KH"
        
        # Tìm tất cả mã khách hàng có prefix KH và extract số
        existing_codes = db.query(User.user_code).filter(
            User.user_code.like(f'{prefix}%')
        ).all()
        
        # Extract tất cả các số hiện có
        existing_numbers = set()
        max_digits = 3  # Bắt đầu với 3 chữ số
        
        for code_tuple in existing_codes:
            if code_tuple[0]:  # code_tuple[0] là giá trị user_code
                try:
                    number_str = code_tuple[0][len(prefix):]  # Bỏ prefix "KH"
                    if number_str.isdigit():
                        number = int(number_str)
                        existing_numbers.add(number)
                        # Cập nhật độ dài tối thiểu cần thiết
                        current_digits = len(number_str)
                        if current_digits > max_digits:
                            max_digits = current_digits
                except (ValueError, IndexError):
                    continue
        
        # Tìm số nhỏ nhất chưa được sử dụng
        next_number = 0
        while next_number in existing_numbers:
            next_number += 1
        
        # Tính toán độ dài cần thiết cho số mới
        required_digits = len(str(next_number))
        if required_digits < max_digits:
            required_digits = max_digits
        
        # Nếu số quá lớn so với độ dài hiện tại, tăng độ dài lên
        if next_number >= (10 ** max_digits):
            required_digits = max_digits + 1
        
        # Tạo mã với độ dài phù hợp
        new_user_code = f"{prefix}{next_number:0{required_digits}d}"
        
        # Double-check không trùng lặp
        existing_user = db.query(User).filter(User.user_code == new_user_code).first()
        if existing_user:
            # Fallback: tìm số tiếp theo
            return generate_user_code_fallback(db, next_number + 1, required_digits, prefix)
        
        return new_user_code
    
    def generate_user_code_fallback(db: Session, start_number: int, min_digits: int, prefix: str) -> str:
        """
        Fallback method: tìm mã khách hàng tiếp theo không bị trùng
        """
        current_number = start_number
        max_attempts = 10000  # Giới hạn số lần thử
        
        for _ in range(max_attempts):
            # Tính độ dài cần thiết
            required_digits = max(min_digits, len(str(current_number)))
            user_code = f"{prefix}{current_number:0{required_digits}d}"
            
            existing_user = db.query(User).filter(User.user_code == user_code).first()
            if not existing_user:
                return user_code
                
            current_number += 1
        
        # Nếu vẫn không tìm được sau max_attempts lần thử
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể tạo mã khách hàng mới sau nhiều lần thử"
        )

    # Tạo người dùng mới với trạng thái PENDING
    user_data = user_in.dict()
    
    # Tạo mã khách hàng
    user_code = generate_user_code(db)
    
    user_create = UserCreateRegister(
        **user_data,
        admin=False,  # Người dùng mới không có quyền admin
        status=UserStatusEnum.PENDING,  # Mặc định là đang chờ xác nhận
        ngay_tao=get_date_time(),
        user_code=user_code  # Thêm mã khách hàng
    )
    user = create(db, obj_in=user_create)
    
    return {
        "message": "Đã tạo yêu cầu đăng ký thành công, chờ admin xác nhận",
        "user_code": user_code,  # Trả về mã khách hàng
        "debug_time": user_create.ngay_tao.isoformat()
    }

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
def get_accepted_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Lấy danh sách người dùng đã được chấp nhận
    Chỉ admin mới có quyền truy cập
    """
    accepted_users = (
        db.query(User)
        .filter(User.status == UserStatus.ACCEPTED)
        .order_by(User.ngay_tao.desc())
        .all()
    )
    return accepted_users

@router.get("/decline-registration", response_model=List[UserStatusInfo])
def get_declined_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Lấy danh sách người dùng bị từ chối đăng ký
    Chỉ admin mới có quyền truy cập
    """
    declined_users = (
        db.query(User)
        .filter(User.status == UserStatus.DECLINE)
        .order_by(User.ngay_tao.desc())
        .all()
    )
    return declined_users


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
    
    try:
        # Lấy access token
        access_token = get_kiot_token()

        id_branch = get_branch_id(access_token)
        
        # Tạo customer trên KiotViet
        add_customer_response = add_customer_to_kiot(
            user_code=updated_user.user_code,
            name=updated_user.ho_ten,
            phone_number=updated_user.so_dien_thoai,
            address=updated_user.dia_chi,
            branch_id=id_branch,  # Thay bằng branch_id thực tế của bạn
            access_token=access_token
        )
        
        # Xử lý response từ KiotViet
        if not add_customer_response.get("success"):
            # Log lỗi nhưng vẫn trả về user đã được approve
            print(f"Warning: Failed to create customer in KiotViet for user {user_id}: {add_customer_response}")
        else:
            print(f"Successfully created customer in KiotViet for user {user_id}")
            
    except Exception as e:
        # Log lỗi nhưng không fail toàn bộ process approve
        print(f"Error integrating with KiotViet for user {user_id}: {str(e)}")
    
    return updated_user

@router.post("/decline-registration/{user_id}", response_model=UserBasicInfo)
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
    user_update = UserUpdate(status=UserStatusEnum.DECLINE)
    updated_user = update(db, db_obj=user, obj_in=user_update)
    
    return updated_user

@router.post("/login/remember", response_model=Token)
def login_remember_me(
    login_data: Login,
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
    )
    # remember_token = crud_token_store.create_token_no_remember(
    #     db=db, 
    #     user_id=user.id, 
    #     expires_days=5,
    # )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": remember_token.token,
        "expires_at": remember_token.expires_at
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