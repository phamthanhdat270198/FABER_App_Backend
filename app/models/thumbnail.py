from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Thumbnail(Base):
    __tablename__ = "thumbnails"

    id = Column(Integer, primary_key=True, index=True)
    type_detail_id = Column(Integer, ForeignKey("type_details.id", ondelete="CASCADE"), nullable=False)
    path_to_thumbnail = Column(String, nullable=False)
    
    # Relationship với TypeDetail sử dụng string reference để tránh circular import
    type_detail = relationship("app.models.type_detail.TypeDetail", back_populates="thumbnails")
    
    def __repr__(self):
        return f"<Thumbnail(id={self.id}, type_detail_id={self.type_detail_id}, path='{self.path_to_thumbnail}')>"