from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class BannerPromote(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    path_to_promote_imgs = Column(Text, nullable=False)
    
    def __repr__(self):
        return f"<Banner Promote(id={self.id},  path='{self.path_to_promote_imgs}')>"