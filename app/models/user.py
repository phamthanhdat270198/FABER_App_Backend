from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String, nullable=False)
    dia_chi = Column(String, nullable=True)
    so_dien_thoai = Column(String, nullable=True)
    diem_thuong = Column(Float, default=0.0)
    
    # Relationship với Order - sử dụng string để tránh circular import
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, ho_ten='{self.ho_ten}', diem_thuong={self.diem_thuong})>"