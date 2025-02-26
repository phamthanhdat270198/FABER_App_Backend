from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    ho_ten = Column(String, nullable=False)
    dia_chi = Column(String, nullable=True)
    so_dien_thoai = Column(String, nullable=True)
    diem_thuong = Column(Integer, default=0)

    def __repr__(self):
        return f"<User(id={self.id}, ho_ten='{self.ho_ten}', diem_thuong={self.diem_thuong})>"
    