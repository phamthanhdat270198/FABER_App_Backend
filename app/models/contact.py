from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.models.base import Base

class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False)
    product_of_interest = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ContactInquiry(id={self.id}, name='{self.name}', product='{self.product_of_interest}')>"