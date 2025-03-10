from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ImageResource(Base):
    __tablename__ = "image_resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_path = Column(String, nullable=False)
    type_detail_id = Column(Integer, ForeignKey("type_details.id", ondelete="CASCADE"), nullable=False)
    
    # Relationship với TypeDetail
    type_detail = relationship("TypeDetail", back_populates="images")
    
    def __repr__(self):
        return f"<ImageResource(id={self.id}, type_detail_id={self.type_detail_id}, image_path='{self.image_path}')>"