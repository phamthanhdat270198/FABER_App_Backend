from sqlalchemy import Column, Integer, String
from app.models.base import Base

class ImageResource(Base):
    __tablename__ = "image_resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_path = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<ImageResource(id={self.id}, image_path='{self.image_path}')>"