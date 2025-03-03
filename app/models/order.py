from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import Base

# Định nghĩa enum cho trạng thái đơn hàng
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPT = "accepted"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationship với User - sử dụng string để tránh circular import
    user = relationship("User", back_populates="orders")
    # Relationship với OrderDetail
    order_details = relationship("OrderDetail", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status}, date_time={self.date_time})>"