from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class PaintType(Base):
    __tablename__ = "paint_types"

    id = Column(Integer, primary_key=True, index=True)
    paint_type = Column(String, nullable=False, unique=True)

    mo_ta_san_pham = Column(Text, nullable=False, default="")
    thanh_phan = Column(Text, nullable=False, default="")
    huong_dan_su_dung = Column(Text, nullable=False, default="")
    luu_y = Column(Text, nullable=True)
    bao_quan = Column(Text, nullable=False, default="")
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationship với TypeDetail
    type_details = relationship("TypeDetail", back_populates="paint_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PaintType(id={self.id}, paint_type='{self.paint_type}', active={self.is_active})>"