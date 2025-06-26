from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone

from app.models.base import Base
def vietnam_time_now():
    # Tạo múi giờ UTC+7
    vn_tz = timezone(timedelta(hours=7))
    # Trả về thời gian hiện tại với múi giờ UTC+7
    return datetime.now(vn_tz)

class TokenStore(Base):
    __tablename__ = "token_store"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    device_info = Column(String, nullable=True)  # Thông tin thiết bị (user-agent, ip, etc.)
    created_at = Column(DateTime, default=vietnam_time_now, nullable=False)
    last_used_at = Column(DateTime, default=vietnam_time_now, nullable=False)
    
    # Relationship với User
    user = relationship("User", back_populates="tokens")
    
    @property
    def is_expired(self):
        """Kiểm tra xem token đã hết hạn chưa"""
        vietnam_timezone = timezone(timedelta(hours=7))
        return vietnam_time_now() > self.expires_at.replace(tzinfo=vietnam_timezone)
    
    @property
    def is_valid(self):
        """Kiểm tra xem token còn hiệu lực không"""
        return not self.is_revoked and not self.is_expired
    
    @classmethod
    def create_for_user(cls, user_id, token, expires_days=30, device_info=None):
        """Tạo token mới cho người dùng với thời hạn mặc định 30 ngày"""
        expires_at = vietnam_time_now() + timedelta(days=expires_days)
        return cls(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_info=device_info
        )
    
    @classmethod
    def create_for_user_no_remember(cls, user_id, token, expires_days=30, device_info=None):
        """Tạo token mới cho người dùng với thời hạn mặc định 30 ngày"""

        expires_at = vietnam_time_now() + timedelta(days=expires_days)
        return cls(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            device_info=device_info
        )
    
    def __repr__(self):
        return f"<TokenStore(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"