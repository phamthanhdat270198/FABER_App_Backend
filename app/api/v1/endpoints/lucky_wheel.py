from typing import Any, List, Optional
import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.crud.crud_user import get, is_admin
from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.rewards_spin import SpinReward
from app.models.rewards_info import RewardInfo, RewardType
from app.schemas.user import SpinInfoResponse, UseSpinResponse
from app.schemas.user import RewardList, SpinRewardBase
from app.db.base import SessionLocal

router = APIRouter()
POINTS_PER_SPIN = 500

db = SessionLocal()
regular_rewards = db.query(RewardInfo.name).filter(
        RewardInfo.type == RewardType.REGULAR,
        RewardInfo.is_active == True
    ).all()
    
# Chuyển đổi kết quả từ danh sách tuple thành danh sách chuỗi
REGULAR_REWARDS = [reward[0] for reward in regular_rewards]

special_rewards_query = db.query(
    RewardInfo.special_spin_number, 
    RewardInfo.name
).filter(
    RewardInfo.type == RewardType.SPECIAL,
    RewardInfo.is_active == True,
    RewardInfo.special_spin_number.isnot(None)
).all()

# Chuyển đổi kết quả thành dictionary
SPECIAL_REWARDS = {int(spin_num): name for spin_num, name in special_rewards_query}

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
    reward_info = db.query(RewardInfo).filter(RewardInfo.name == reward_type).first()

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
            reward_type=reward_type,
            reward_img=reward_info.image_url
        )

@router.get("/rewards_list", response_model=RewardList)
def get_grouped_rewards(
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách phần thưởng được nhóm theo loại (regular và special)
    
    - **is_active**: Chỉ lấy các phần thưởng đang hoạt động
    """
    # Lấy phần thưởng thông thường
    regular_rewards = db.query(RewardInfo).filter(
        RewardInfo.is_active == is_active,
        RewardInfo.type == RewardType.REGULAR
    ).all()

    ignore_rewards = db.query(RewardInfo).filter(
        RewardInfo.is_active == is_active,
        RewardInfo.type == RewardType.IGNORE
    ).all()
    
    # Lấy phần thưởng đặc biệt
    special_rewards = db.query(RewardInfo).filter(
        RewardInfo.is_active == is_active,
        RewardInfo.type == RewardType.SPECIAL
    ).all()
    
    # Tổng số phần thưởng
    total_count = len(regular_rewards) + len(special_rewards) + len(ignore_rewards)
    
    return {
        "regular_rewards": regular_rewards,
        "special_rewards": special_rewards,
        "ignore_rewards": ignore_rewards,
        "total_count": total_count
    }

@router.get("/spin-rewards/me/", response_model=List[SpinRewardBase])
def get_my_spin_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách phần thưởng của người dùng hiện tại.
    """
    # Tạo query cơ bản
    rewards = db.query(SpinReward).filter(SpinReward.user_id == current_user.id)
    
    return rewards

@router.patch("/spin-rewards/{reward_id}/claim", response_model=SpinRewardBase)
def claim_spin_reward(
    reward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Xác nhận đã nhận phần thưởng (claim).
    
    Args:
        reward_id: ID của phần thưởng cần xác nhận
        request: Dữ liệu bổ sung cho việc xác nhận (tuỳ chọn)
        db: Database session
        current_user: Người dùng hiện tại
    
    Returns:
        Thông tin phần thưởng đã được cập nhật
    """
    # Tìm phần thưởng theo ID
    reward = db.query(SpinReward).filter(SpinReward.id == reward_id).first()
    
    # Kiểm tra phần thưởng có tồn tại không
    if not reward:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy phần thưởng với ID {reward_id}"
        )
    
    # Kiểm tra phần thưởng đã được xác nhận chưa
    if reward.is_claimed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Phần thưởng này đã được xác nhận nhận vào lúc {reward.claimed_at}"
        )
    
    # Cập nhật trạng thái đã nhận và thời gian nhận
    reward.is_claimed = True
    reward.claimed_at = datetime.utcnow()
    
    # Lưu thay đổi vào database
    db.commit()
    db.refresh(reward)
    
    return reward