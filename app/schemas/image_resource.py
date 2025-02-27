from pydantic import BaseModel, Field
import uuid
from typing import Optional

class ImageResourceBase(BaseModel):
    image_path: str

class ImageResourceCreate(ImageResourceBase):
    uuid: Optional[str] = Field(None, description="Nếu không cung cấp, hệ thống sẽ tự động tạo UUID")

class ImageResourceUpdate(BaseModel):
    image_path: Optional[str] = None

class ImageResourceResponse(ImageResourceBase):
    uuid: str
    
    class Config:
        orm_mode = True