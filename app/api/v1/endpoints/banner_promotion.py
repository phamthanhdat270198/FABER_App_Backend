from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.banner_promotion import BannerPromote
from app.api.deps import get_db
from app.schemas.banner_promotion import BannerPromoteResponse

router = APIRouter()

@router.get("/banner-promotes/", response_model=List[BannerPromoteResponse])
async def get_all_banner_promotes(db: Session = Depends(get_db)):
    """
    Get a list of all banner promotes.
    
    Returns:
        List[BannerPromoteResponse]: A list of all banner promote images
    """
    banner_promotes = db.query(BannerPromote).all()
    return banner_promotes