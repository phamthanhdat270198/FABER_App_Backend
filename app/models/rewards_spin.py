from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class SpinReward(Base):
    __tablename__ = "spin_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reward_type = Column(String, nullable=False)  # Loại phần quà
    is_claimed = Column(Boolean, default=False)
    spin_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    claimed_at = Column(DateTime, nullable=True)
    
    # Relationship với User
    user = relationship("User", back_populates="spin_reward")
    
    
    def __repr__(self):
        return f"<SpinReward(id={self.id}, user_id={self.user_id}, reward_type='{self.reward_type}', spin_number={self.spin_number})>"
