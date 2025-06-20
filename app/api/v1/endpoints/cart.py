from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import and_

from app.models.cart import Cart
from app.models.cart_items import CartItem
from app.models.type_detail import TypeDetail
from app.models.thumbnail import Thumbnail
from app.models.image_resource import ImageResource
from app.schemas.cart_items import OrderCreate, OrderResponse, DeleteIDCart
from app.models.user import User
from app.db.base import get_db
from app.api.deps import get_current_active_user
from app.schemas.cart_items import CartItemCreate, CartItemResponse,CartItemThumbnailResponse, UnpaidOrderItemResponse, UnpaidOrderHistoryResponse, paidOrderItemResponse, PaidOrderHistoryResponse

from app.api.deps import get_db, get_current_user, get_current_admin_user

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
        existing_item.quantity += item.quantity
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
            reward=item.quantity * type_detail.bonus_points,
            code=type_detail.code
            
        ))
    
    return result

@router.delete("/detete", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    delete_ids: DeleteIDCart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if not delete_ids.delete_ids or len(delete_ids.delete_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có sản phẩm nào được chọn để xóa"
        )
    
    # Lấy các mặt hàng từ giỏ hàng của user hiện tại
    
    cart_items = db.query(CartItem).join(Cart).filter(
        Cart.user_id == current_user.id,
        CartItem.id.in_(delete_ids.delete_ids),
        CartItem.is_active == True
    ).all()
    # print("cart_items", cart_items)
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sản phẩm cần xóa nào trong giỏ hàng của bạn"
        )
    
    # Xóa mềm sản phẩm khỏi giỏ hàng
    for cart_item in cart_items:
        cart_item.is_active = False
    db.commit()
    
    return None

@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item_quantity(
    item_id: int,
    quantity: int,
    color_code: str,
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
    cart_item.color_code = color_code
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
    total_points = 0
    items_count = len(cart_items)
    
    # Chuyển trạng thái từng mặt hàng sang False
    for item in cart_items:
        # Tính giá từ type_detail và số lượng
        type_detail = db.query(TypeDetail).filter(TypeDetail.id == item.type_detail_id).first()
        price = type_detail.price * item.quantity if type_detail.price else 0
        total_amount += price
        total_points += type_detail.bonus_points
        # Cập nhật trạng thái
        item.is_active = False
        item.modified_at = datetime.utcnow()
    #fb 01 32 23 505 +2
    #fb 102 33, 350, 365, 25, 536, 845 + 7/ thung va 2d / lon 5l
    # fb 381, 545, m11, m35, ac500, pu100 +10/thung va +3/lon
    # fb m12, m38 +15/thung va 3d/lon 5l
    # Tính điểm thưởng (ví dụ: 1% tổng giá trị đơn hàng)
    
    # Cộng điểm thưởng cho người dùng
    # current_user.diem_thuong += total_points
    
    # Lưu các thay đổi vào database
    db.commit()
    
    return OrderResponse(
        message="Đặt hàng thành công",
        items_count=items_count,
        total_amount=total_amount,
        reward_points_earned=total_points,
        total_reward_points=current_user.diem_thuong
    )

@router.get("/unpaid-orders", response_model=UnpaidOrderHistoryResponse, status_code=status.HTTP_200_OK)
def get_unpaid_order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    API lấy lịch sử đơn hàng chưa thanh toán
    
    Trả về danh sách các sản phẩm đã đặt hàng nhưng chưa thanh toán:
    - Các cart item có is_active = False (đã đặt hàng)
    - Chưa có is_purchase = True (chưa thanh toán)
    """
    
    # Query các cart item đã đặt hàng nhưng chưa thanh toán
    unpaid_items = db.query(CartItem, TypeDetail, ImageResource).join(
        Cart, CartItem.cart_id == Cart.id
    ).join(
        TypeDetail, CartItem.type_detail_id == TypeDetail.id
    ).outerjoin(
        ImageResource, TypeDetail.id == ImageResource.type_detail_id
    ).filter(
        and_(
            Cart.user_id == current_user.id,
            CartItem.is_active == False,  # Đã đặt hàng
            CartItem.is_purchase == False  # Chưa thanh toán
        )
    ).order_by(CartItem.modified_at.desc()).all()
    
    if not unpaid_items:
        return UnpaidOrderHistoryResponse(
            message="Không có đơn hàng chưa thanh toán nào",
            total_items=0,
            total_amount=0.0,
            orders=[]
        )
    
    # Xử lý dữ liệu response
    order_items = []
    total_amount = 0.0
    total_points = 0
    for cart_item, type_detail, image_resource in unpaid_items:
        unit_price = type_detail.price if type_detail.price else 0.0
        total_price = unit_price * cart_item.quantity
        total_amount += total_price
        image_path = image_resource.image_path if image_resource else ""
        
        
        order_item = UnpaidOrderItemResponse(
            id=cart_item.id,
            product=type_detail.product,
            code=type_detail.code if type_detail.code else "N/A",
            volume=cart_item.volume,
            color_code=cart_item.color_code,
            quantity=cart_item.quantity,
            order_date=cart_item.modified_at,
            total_price=total_price,
            # unit_price=unit_price
            image_path=image_path
        )
        order_items.append(order_item)
    
    return UnpaidOrderHistoryResponse(
        message="Lấy lịch sử đơn hàng chưa thanh toán thành công",
        total_items=len(order_items),
        total_amount=total_amount,
        orders=order_items
    )

@router.get("/paid-orders", response_model=PaidOrderHistoryResponse, status_code=status.HTTP_200_OK)
def get_unpaid_order_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    API lấy lịch sử đơn hàng chưa thanh toán
    
    Trả về danh sách các sản phẩm đã đặt hàng nhưng chưa thanh toán:
    - Các cart item có is_active = False (đã đặt hàng)
    - Chưa có is_purchase = True (chưa thanh toán)
    """
    
    # Query các cart item đã đặt hàng nhưng chưa thanh toán
    unpaid_items = db.query(CartItem, TypeDetail, ImageResource).join(
        Cart, CartItem.cart_id == Cart.id
    ).join(
        TypeDetail, CartItem.type_detail_id == TypeDetail.id
    ).outerjoin(
        ImageResource, TypeDetail.id == ImageResource.type_detail_id
    ).filter(
        and_(
            Cart.user_id == current_user.id,
            CartItem.is_active == False,  # Đã đặt hàng
            CartItem.is_purchase == True  # Chưa thanh toán
        )
    ).order_by(CartItem.modified_at.desc()).all()
    
    if not unpaid_items:
        return UnpaidOrderHistoryResponse(
            message="Không có đơn hàng chưa thanh toán nào",
            total_items=0,
            total_amount=0.0,
            orders=[]
        )
    
    # Xử lý dữ liệu response
    order_items = []
    total_amount = 0.0
    total_points = 0
    
    for cart_item, type_detail, image_resource in unpaid_items:
        unit_price = type_detail.price if type_detail.price else 0.0
        total_price = unit_price * cart_item.quantity
        total_amount += total_price
        image_path = image_resource.image_path if image_resource else ""
        total_points += type_detail.bonus_points
        
        order_item = paidOrderItemResponse(
            id=cart_item.id,
            product=type_detail.product,
            code=type_detail.code if type_detail.code else "N/A",
            volume=cart_item.volume,
            color_code=cart_item.color_code,
            quantity=cart_item.quantity,
            order_date=cart_item.modified_at,
            total_price=total_price,
            # unit_price=unit_price
            image_path=image_path,
            bonus_points=total_points
        )
        order_items.append(order_item)
    
    return PaidOrderHistoryResponse(
        message="Lấy lịch sử đơn hàng chưa thanh toán thành công",
        total_items=len(order_items),
        total_amount=total_amount,
        orders=order_items
    )

# @router.patch("/admin/update-unpaid-order", response_model=AdminUpdateResponse)
# def admin_update_unpaid_order(
#     request: BatchUpdateRequest,
#     db: Session = Depends(get_db),
#     current_admin: User = Depends(get_current_admin_user)  # Chỉ admin mới được dùng
# ):
#     """
#     API cho admin cập nhật thông tin đơn hàng chưa thanh toán
    
#     Admin có thể sửa:
#     - Tên sản phẩm (cập nhật trong TypeDetail)
#     - Số lượng sản phẩm
#     - Mã màu
#     - Kích thước
    
#     Sau đó tính lại điểm thưởng và cập nhật cho user
#     """
    
#     if not request.updates:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Danh sách cập nhật không được để trống"
#         )
    
#     # Kiểm tra user tồn tại
#     target_user = db.query(User).filter(User.id == request.user_id).first()
#     if not target_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Không tìm thấy user với ID: {request.user_id}"
#         )
    
#     # Lấy danh sách cart_item_ids cần cập nhật
#     cart_item_ids = [update.cart_item_id for update in request.updates]
    
#     # Query các cart item chưa thanh toán của user
#     cart_items_data = db.query(CartItem, TypeDetail).join(
#         Cart, CartItem.cart_id == Cart.id
#     ).join(
#         TypeDetail, CartItem.type_detail_id == TypeDetail.id
#     ).filter(
#         and_(
#             Cart.user_id == request.user_id,
#             CartItem.id.in_(cart_item_ids),
#             CartItem.is_active == False,  # Đã đặt hàng
#             CartItem.is_purchase == False  # Chưa thanh toán
#         )
#     ).all()
    
#     if not cart_items_data:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Không tìm thấy đơn hàng chưa thanh toán nào phù hợp"
#         )
    
#     # Tạo dict để tra cứu nhanh
#     items_dict = {cart_item.id: (cart_item, type_detail) for cart_item, type_detail in cart_items_data}
    
#     # Kiểm tra tất cả cart_item_ids có tồn tại không
#     found_ids = set(items_dict.keys())
#     requested_ids = set(cart_item_ids)
#     missing_ids = requested_ids - found_ids
    
#     if missing_ids:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Không tìm thấy cart item với ID: {list(missing_ids)}"
#         )
    
#     # Tính điểm thưởng cũ
#     old_total_bonus_points = sum(
#         (type_detail.bonus_points or 0) * cart_item.quantity 
#         for cart_item, type_detail in cart_items_data
#     )
    
#     updated_items = []
    
#     # Xử lý từng cập nhật
#     for update_request in request.updates:
#         cart_item, type_detail = items_dict[update_request.cart_item_id]
        
#         # Lưu giá trị cũ
#         old_product = type_detail.product
#         old_quantity = cart_item.quantity
#         old_color_code = cart_item.color_code
#         old_volume = cart_item.volume
#         old_bonus_points = (type_detail.bonus_points or 0) * cart_item.quantity
        
#         # Cập nhật TypeDetail (tên sản phẩm)
#         if update_request.product_name is not None:
#             type_detail.product = update_request.product_name
        
#         # Cập nhật CartItem
#         if update_request.quantity is not None:
#             cart_item.quantity = update_request.quantity
            
#         if update_request.color_code is not None:
#             cart_item.color_code = update_request.color_code
            
#         if update_request.volume is not None:
#             cart_item.volume = update_request.volume
        
#         # Cập nhật modified_at
#         cart_item.modified_at = datetime.utcnow()
        
#         # Tính điểm thưởng mới
#         new_bonus_points = (type_detail.bonus_points or 0) * cart_item.quantity
        
#         # Tính thay đổi giá (nếu có)
#         old_price = (type_detail.price or 0) * old_quantity
#         new_price = (type_detail.price or 0) * cart_item.quantity
#         price_change = new_price - old_price
        
#         # Thêm vào danh sách response
#         updated_items.append(UpdatedItemResponse(
#             cart_item_id=cart_item.id,
#             old_product=old_product,
#             new_product=type_detail.product,
#             old_quantity=old_quantity,
#             new_quantity=cart_item.quantity,
#             old_color_code=old_color_code,
#             new_color_code=cart_item.color_code,
#             old_volume=old_volume,
#             new_volume=cart_item.volume,
#             old_bonus_points=old_bonus_points,
#             new_bonus_points=new_bonus_points,
#             price_change=price_change
#         ))
    
#     # Tính lại tổng điểm thưởng mới
#     new_total_bonus_points = sum(
#         (type_detail.bonus_points or 0) * cart_item.quantity 
#         for cart_item, type_detail in cart_items_data
#     )
    
#     # Cập nhật điểm thưởng cho user
#     bonus_points_difference = new_total_bonus_points - old_total_bonus_points
#     if hasattr(target_user, 'diem_thuong'):
#         target_user.diem_thuong = (target_user.diem_thuong or 0) + bonus_points_difference
    
#     # Lưu tất cả thay đổi
#     db.commit()
    
#     return AdminUpdateResponse(
#         message="Cập nhật đơn hàng thành công",
#         updated_items=updated_items,
#         total_items_updated=len(updated_items),
#         old_total_bonus_points=old_total_bonus_points,
#         new_total_bonus_points=new_total_bonus_points,
#         bonus_points_difference=bonus_points_difference
#     )

# @router.get("/admin/unpaid-orders/{user_id}")
# def admin_get_user_unpaid_orders(
#     user_id: int,
#     db: Session = Depends(get_db),
#     current_admin: User = Depends(get_current_admin_user)
# ):
#     """
#     API cho admin xem đơn hàng chưa thanh toán của một user cụ thể
#     """
    
#     # Kiểm tra user tồn tại
#     target_user = db.query(User).filter(User.id == user_id).first()
#     if not target_user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Không tìm thấy user với ID: {user_id}"
#         )
    
#     # Query đơn hàng chưa thanh toán
#     unpaid_items = db.query(CartItem, TypeDetail).join(
#         Cart, CartItem.cart_id == Cart.id
#     ).join(
#         TypeDetail, CartItem.type_detail_id == TypeDetail.id
#     ).filter(
#         and_(
#             Cart.user_id == user_id,
#             CartItem.is_active == False,  # Đã đặt hàng
#             CartItem.is_purchase == False  # Chưa thanh toán
#         )
#     ).order_by(CartItem.modified_at.desc()).all()
    
#     if not unpaid_items:
#         return {
#             "message": f"User {target_user.username if hasattr(target_user, 'username') else user_id} không có đơn hàng chưa thanh toán",
#             "user_id": user_id,
#             "orders": []
#         }
    
#     # Format response
#     orders = []
#     for cart_item, type_detail in unpaid_items:
#         orders.append({
#             "cart_item_id": cart_item.id,
#             "product": type_detail.product,
#             "code": type_detail.code,
#             "quantity": cart_item.quantity,
#             "color_code": cart_item.color_code,
#             "volume": cart_item.volume,
#             "price": type_detail.price,
#             "bonus_points": type_detail.bonus_points,
#             "order_date": cart_item.modified_at,
#             "total_price": (type_detail.price or 0) * cart_item.quantity,
#             "total_bonus_points": (type_detail.bonus_points or 0) * cart_item.quantity
#         })
    
#     return {
#         "message": "Lấy danh sách đơn hàng thành công",
#         "user_id": user_id,
#         "total_items": len(orders),
#         "orders": orders
#     }