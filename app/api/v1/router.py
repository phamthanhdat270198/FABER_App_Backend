from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, profile
from app.api.v1.endpoints import products
from app.api.v1.endpoints import images
from app.api.v1.endpoints import paint_type_management
from app.api.v1.endpoints import cart
from app.api.v1.endpoints import contact
from app.api.v1.endpoints import lucky_wheel

api_router = APIRouter()

# Thêm các router từ các modules endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(paint_type_management.router, prefix="/paint-types", tags=["paint-types"])
api_router.include_router(cart.router, prefix="/cart", tags=["carts"])
api_router.include_router(contact.router, prefix="/contact", tags=["contacts"])
api_router.include_router(lucky_wheel.router, prefix="/lucky_wheel", tags=["lucky_wheel"])
