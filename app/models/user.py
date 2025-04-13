from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.base import Base

import enum

class UserStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String, nullable=False)
    dia_chi = Column(String, nullable=True)
    so_dien_thoai = Column(String, nullable=True)
    diem_thuong = Column(Float, default=0.0)
    ngay_tao = Column(DateTime, default=datetime.utcnow, nullable=False)
    admin = Column(Boolean, default=False, nullable=False)
    hashed_password = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    kth_spin = Column(Integer, default=0)
    
    # Relationship với Order - sử dụng string để tránh circular import
    tokens = relationship("TokenStore", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan" )

    def __repr__(self):
        return f"<User(id={self.id}, ho_ten='{self.ho_ten}', diem_thuong={self.diem_thuong})>"