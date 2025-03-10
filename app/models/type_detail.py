from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.models.base import Base

class TypeDetail(Base):
    __tablename__ = "type_details"

    id = Column(Integer, primary_key=True, index=True)
    paint_type_id = Column(Integer, ForeignKey("paint_types.id"), nullable=False)
    product = Column(String, nullable=False)
    code = Column(String, nullable=True)
    package = Column(String, nullable=True)
    volume = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    m2_cover = Column(Float, nullable=True)
    promotion = Column(String, nullable=True)
    base64 = Column(Text, nullable=True)
    
    # Relationship với PaintType
    paint_type = relationship("PaintType", back_populates="type_details")
    
    # Relationship với OrderDetail
    order_details = relationship("OrderDetail", back_populates="type_detail")

    # Relationship với ImageResource
    images = relationship("ImageResource", back_populates="type_detail", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TypeDetail(id={self.id}, product='{self.product}', paint_type_id={self.paint_type_id})>"