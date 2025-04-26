from pydantic import BaseModel

class BannerPromoteBase(BaseModel):
    path_to_promote_imgs: str

class BannerPromoteCreate(BannerPromoteBase):
    pass

class BannerPromoteResponse(BannerPromoteBase):
    id: int
    
    class Config:
        orm_mode = True
        from_attributes = True