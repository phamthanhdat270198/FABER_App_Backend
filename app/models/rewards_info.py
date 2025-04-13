from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base

class RewardType(str, enum.Enum):
    REGULAR = "REGULAR"
    SPECIAL = "SPECIAL"
    IGNORE = "IGNORE"

class RewardInfo(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(RewardType), default=RewardType.REGULAR, nullable=False)
    is_special = Column(Boolean, default=False, nullable=False)
    special_spin_number = Column(Integer, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    

    def __repr__(self):
        return f"<RewardInfo(id={self.id}, name='{self.name}', type='{self.type}', is_special={self.is_special})>"