from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class PaintType(Base):
    __tablename__ = "paint_types"

    id = Column(Integer, primary_key=True, index=True)
    paint_type = Column(String, nullable=False, unique=True)
    
    # Relationship với TypeDetail
    type_details = relationship("TypeDetail", back_populates="paint_type", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PaintType(id={self.id}, paint_type='{self.paint_type}')>"