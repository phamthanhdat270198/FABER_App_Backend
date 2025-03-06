from pydantic import BaseModel, Field
from typing import Optional

class ImageResourceBase(BaseModel):
    image_path: str

class ImageResourceCreate(ImageResourceBase):
    pass

class ImageResourceUpdate(BaseModel):
    image_path: Optional[str] = None

class ImageResourceResponse(ImageResourceBase):
    id: int
    
    class Config:
        orm_mode = True