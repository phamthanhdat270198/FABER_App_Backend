# app/models/image_resource.py
from sqlalchemy import Column, String
import uuid

from app.models.base import Base

class ImageResource(Base):
    __tablename__ = "image_resources"

    uuid = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    image_path = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<ImageResource(uuid={self.uuid}, image_path='{self.image_path}')>"