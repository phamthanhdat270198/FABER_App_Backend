# Thêm vào file models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class SpinReward(Base):
    __tablename__ = "spin_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_type = Column(String, nullable=False)  # Loại phần quà: điểm, voucher, sản phẩm, ...
    is_claimed = Column(Boolean, default=False)   # Đã nhận thưởng chưa
    spin_number = Column(Integer, nullable=False) # Lần quay thứ mấy
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    claimed_at = Column(DateTime, nullable=True)  # Thời gian nhận thưởng
    
    # Relationship với User
    user = relationship("User", backref="spin_rewards")
    
    def __repr__(self):
        return f"<SpinReward(id={self.id}, user_id={self.user_id}, reward_type='{self.reward_type}', reward_value={self.reward_value})>"
