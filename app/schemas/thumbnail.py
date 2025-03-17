from pydantic import BaseModel
from typing import Optional

class ThumbnailBase(BaseModel):
    path_to_thumbnail: str

class ThumbnailCreate(ThumbnailBase):
    type_detail_id: int

class ThumbnailUpdate(ThumbnailBase):
    path_to_thumbnail: Optional[str] = None

class Thumbnail(ThumbnailBase):
    id: int
    type_detail_id: int

    class Config:
        orm_mode = True