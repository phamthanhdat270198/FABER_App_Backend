from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.models.cart import Cart
from app.models.cart_items import CartItem
from app.models.type_detail import TypeDetail
from app.models.thumbnail import Thumbnail
from app.schemas.cart_items import OrderCreate, OrderResponse
from app.models.user import User
from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.schemas.cart_items import CartItemCreate, CartItemResponse,CartItemThumbnailResponse


router = APIRouter()
REWARD = 10

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Kiểm tra xem type_detail_id có tồn tại không
    type_detail = db.query(TypeDetail).filter(TypeDetail.id == item.product_id).first()
    if not type_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với id {item.product_id} không tồn tại"
        )
    
    # Kiểm tra xem type_detail có hỗ trợ dung tích này không
    if type_detail.volume and item.volume != type_detail.volume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sản phẩm này không hỗ trợ dung tích {item.volume}"
        )
    
    # Tìm hoặc tạo giỏ hàng nếu chưa có
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.is_active == True
    ).first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.type_detail_id == item.product_id,
        CartItem.color_code == item.color_code,
        CartItem.volume == item.volume,
        CartItem.is_active == True
    ).first()
    
    if existing_item:
        # Cập nhật số lượng nếu sản phẩm đã tồn tại
        # co the thay doi cho phu hop voi nhu cau
        existing_item.quantity == item.quantity
        db.commit()
        db.refresh(existing_item)
        
        return CartItemResponse(
            id=existing_item.id,
            product_id=existing_item.product_id,
            color_code=existing_item.color_code,
            volume=existing_item.volume,
            quantity=existing_item.quantity,
            product=type_detail.product,
            price=type_detail.price or 0
        )
    else:
        # Tạo mới cart item nếu chưa tồn tại
        new_cart_item = CartItem(
            cart_id=cart.id,
            type_detail_id=item.product_id,
            color_code=item.color_code,
            volume=item.volume,
            quantity=item.quantity
        )
        
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        
        return CartItemResponse(
            id=new_cart_item.id,
            product_id=new_cart_item.type_detail_id,
            color_code=new_cart_item.color_code,
            volume=new_cart_item.volume,
            quantity=new_cart_item.quantity,
            product=type_detail.product,
            price=type_detail.price or 0
        )

@router.get("/items", response_model=List[CartItemThumbnailResponse])
def get_cart_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Tìm giỏ hàng hiện tại của người dùng
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.is_active == True
    ).first()
    
    if not cart:
        return []
    
    # Lấy tất cả các sản phẩm trong giỏ hàng
    cart_items = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.is_active == True
    ).all()
    
    result = []
    for item in cart_items:
        type_detail = db.query(TypeDetail).filter(TypeDetail.id == item.type_detail_id).first()
        thumbnails = db.query(Thumbnail).filter(Thumbnail.type_detail_id == item.type_detail_id).all()
        thumbnail_path = thumbnails[0].path_to_thumbnail
        result.append(CartItemThumbnailResponse(
            id=item.id,
            product_id=item.type_detail_id,
            color_code=item.color_code,
            volume=item.volume,
            quantity=item.quantity,
            product=type_detail.product,
            price=type_detail.price or 0, 
            thumbnail=thumbnail_path,
            reward=item.quantity * REWARD
            
        ))
    
    return result

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Tìm giỏ hàng hiện tại của người dùng
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.is_active == True
    ).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giỏ hàng không tồn tại"
        )
    
    # Tìm sản phẩm cần xóa
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id,
        CartItem.is_active == True
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với id {item_id} không tồn tại trong giỏ hàng"
        )
    
    # Xóa mềm sản phẩm khỏi giỏ hàng
    cart_item.is_active = False
    db.commit()
    
    return None

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item_quantity(
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số lượng phải lớn hơn 0"
        )
    
    # Tìm giỏ hàng hiện tại của người dùng
    cart = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.is_active == True
    ).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Giỏ hàng không tồn tại"
        )
    
    # Tìm sản phẩm cần cập nhật
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id,
        CartItem.is_active == True
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sản phẩm với id {item_id} không tồn tại trong giỏ hàng"
        )
    
    # Cập nhật số lượng
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    
    type_detail = db.query(TypeDetail).filter(TypeDetail.id == cart_item.type_detail_id).first()
    
    return CartItemResponse(
        id=cart_item.id,
        product_id=cart_item.type_detail_id,
        color_code=cart_item.color_code,
        volume=cart_item.volume,
        quantity=cart_item.quantity,
        product=type_detail.product,
        price=type_detail.price or 0
    )

@router.post("/place-order", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    API đặt hàng:
    - Chuyển trạng thái các mặt hàng đã chọn trong giỏ hàng sang không hoạt động (is_active = False)
    - Cộng điểm thưởng cho người dùng
    """
    # Kiểm tra nếu không có sản phẩm nào được chọn
    if not order.cart_item_ids or len(order.cart_item_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có sản phẩm nào được chọn để đặt hàng"
        )
    
    # Lấy các mặt hàng từ giỏ hàng của user hiện tại
    cart_items = db.query(CartItem).join(Cart).filter(
        Cart.user_id == current_user.id,
        CartItem.id.in_(order.cart_item_ids),
        CartItem.is_active == True
    ).all()
    
    # Kiểm tra nếu không tìm thấy sản phẩm nào
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm nào trong giỏ hàng của bạn"
        )
    
    # Kiểm tra xem số lượng sản phẩm tìm được có khớp với số lượng sản phẩm yêu cầu không
    if len(cart_items) != len(order.cart_item_ids):
        # Có một số sản phẩm không thuộc giỏ hàng của người dùng hoặc không còn hoạt động
        found_ids = [item.id for item in cart_items]
        missing_ids = [id for id in order.cart_item_ids if id not in found_ids]
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy sản phẩm với id: {missing_ids}"
        )

    # Tính tổng số tiền và điểm thưởng
    total_amount = 0
    items_count = len(cart_items)
    
    # Chuyển trạng thái từng mặt hàng sang False
    for item in cart_items:
        # Tính giá từ type_detail và số lượng
        type_detail = db.query(TypeDetail).filter(TypeDetail.id == item.type_detail_id).first()
        price = type_detail.price * item.quantity if type_detail.price else 0
        total_amount += price
        
        # Cập nhật trạng thái
        item.is_active = False
        item.modified_at = datetime.utcnow()
    
    # Tính điểm thưởng (ví dụ: 1% tổng giá trị đơn hàng)
    reward_points = total_amount * REWARD
    
    # Cộng điểm thưởng cho người dùng
    current_user.diem_thuong += reward_points
    
    # Lưu các thay đổi vào database
    db.commit()
    
    return OrderResponse(
        message="Đặt hàng thành công",
        items_count=items_count,
        total_amount=total_amount,
        reward_points_earned=reward_points,
        total_reward_points=current_user.diem_thuong
    )
