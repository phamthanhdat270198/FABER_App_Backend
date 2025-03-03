from fastapi import APIRouter

from app.api.v1.endpoints import auth

api_router = APIRouter()

# Thêm các router từ các modules endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Thêm router cho các endpoints khác khi cần
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"])