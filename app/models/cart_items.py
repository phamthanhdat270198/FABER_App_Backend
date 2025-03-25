from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    type_detail_id = Column(Integer, ForeignKey("type_details.id"), nullable=False)
    color_code = Column(String, nullable=False)  # Mã màu
    volume = Column(Float, nullable=False)       # Dung tích
    quantity = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationship với Cart
    cart = relationship("Cart", back_populates="cart_items")
    
    # Relationship với TypeDetail
    type_detail = relationship("TypeDetail", back_populates="cart_items")

    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, type_detail_id={self.type_detail_id}, color_code='{self.color_code}', volume={self.volume})>"