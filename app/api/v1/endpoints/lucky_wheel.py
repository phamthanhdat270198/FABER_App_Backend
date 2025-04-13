from typing import Any, List
import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.crud_user import get, is_admin
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.rewards import SpinReward
from app.schemas.user import SpinInfoResponse, UseSpinResponse

router = APIRouter()
POINTS_PER_SPIN = 500


# Danh sách phần quà thông thường (random)
REGULAR_REWARDS = [
    "Nồi chiên không dầu",
    "Máy lọc không khí",
    "Máy hút bụi cầm tay",
    "2 thùng sơn lót nội thất cao cấp"
]

# Phần quà đặc biệt dựa vào kth_spin
SPECIAL_REWARDS = {
    5: "Nửa chỉ vàng",
    9: "1 chỉ vàng",
    15: "Xe Vision"
}   

@router.get("/spin-info", response_model=SpinInfoResponse)
def get_user_spin_info(current_user: User = Depends(get_current_user),
                        db: Session = Depends(get_db)
):
    """
    Trả về thông tin về lượt quay của người dùng, bao gồm:
    - Số lượt quay có thể dùng (dựa trên điểm thưởng)
    - Tổng số lượt quay đã thực hiện (kth_spin)
    """
    # Lấy thông tin người dùng từ database
    user = db.query(User).filter(User.id == current_user.id).first()
    
    # Tính toán số lượt quay dựa trên điểm thưởng
    available_spins = int(user.diem_thuong // POINTS_PER_SPIN)
    
    return SpinInfoResponse(
        id = current_user.id,
        nums_spin=available_spins,
        kth_spin=user.kth_spin
    )

@router.post("/spin", response_model=UseSpinResponse)
def use_spin(current_user: User = Depends(get_current_user)
             , db: Session = Depends(get_db)):
    """
    Sử dụng một lượt quay cho người dùng:
    - Kiểm tra xem người dùng có đủ điểm để sử dụng lượt quay không
    - Giảm điểm thưởng đi 500 nếu sử dụng lượt quay
    - Tăng kth_spin lên 1
    """
    # Lấy thông tin người dùng từ database
    user = db.query(User).filter(User.id == current_user.id).first()
    
    # Kiểm tra xem người dùng có đủ điểm để sử dụng lượt quay không
    if user.diem_thuong < POINTS_PER_SPIN:
        return UseSpinResponse(
            success=False,
            new_kth_spin=user.kth_spin,
            remaining_spins=0,
            message=f"Không đủ điểm thưởng. Cần {POINTS_PER_SPIN} điểm cho một lượt quay."
        )
    
    # Trừ điểm thưởng và tăng kth_spin
    user.diem_thuong -= POINTS_PER_SPIN
    user.kth_spin += 1

    # Xác định phần quà dựa vào kth_spin hiện tại
    current_spin = user.kth_spin
    
    # Kiểm tra xem có phải lượt quay đặc biệt không
    if current_spin in SPECIAL_REWARDS:
        reward_type = SPECIAL_REWARDS[current_spin]
    else:
        # Nếu không phải lượt quay đặc biệt, chọn ngẫu nhiên từ danh sách phần quà thông thường
        reward_type = random.choice(REGULAR_REWARDS)
    
    # Tạo bản ghi phần quà trong database
    reward = SpinReward(
        user_id=user.id,
        reward_type=reward_type,
        spin_number=current_spin
    )
    
    # Cập nhật database
    db.add(reward)
    db.commit()
    db.refresh(reward)
    
    # Tính số lượt quay còn lại
    remaining_spins = int(user.diem_thuong // POINTS_PER_SPIN)
    
    return UseSpinResponse(
            success=True,
            new_kth_spin=current_spin,
            remaining_spins=remaining_spins,
            message=f"Chúc mừng! Bạn đã nhận được: {reward_type}",
            reward_type=reward_type
        )