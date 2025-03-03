from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base

class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    type_detail_id = Column(Integer, ForeignKey("type_details.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False)
    
    # Relationship với Order
    order = relationship("Order", back_populates="order_details")
    
    # Relationship với TypeDetail
    type_detail = relationship("TypeDetail", back_populates="order_details")
    
    def __repr__(self):
        return f"<OrderDetail(id={self.id}, order_id={self.order_id}, type_detail_id={self.type_detail_id}, quantity={self.quantity})>"