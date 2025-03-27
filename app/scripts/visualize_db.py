import os
import sys
from tabulate import tabulate  # Cài đặt với: pip install tabulate
from datetime import datetime

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
print("current dir = ", current_dir)
app_dir = os.path.dirname(current_dir)
print("app dir = ", app_dir)
root_dir = os.path.dirname(app_dir)
print("root dir == ", root_dir)
sys.path.append(root_dir)

from app.db.base import SessionLocal
# from app.models.order import Order
from app.models.user import User
from app.models.paint_type import PaintType
from app.models.image_resource import ImageResource
from app.models.type_detail import TypeDetail
# from app.models.order_detail import OrderDetail 
from app.models.token_store import TokenStore
from app.models.cart import Cart
from app.models.cart_items import CartItem


from sqlalchemy.orm import joinedload
from sqlalchemy import func


def show_users():
    db = SessionLocal()
    try:
        # Lấy tất cả người dùng từ database
        users = db.query(User).all()
        
        if not users:
            print("Không có dữ liệu người dùng trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["ID", "Họ Tên", "Số điện thoại", "Điểm thưởng", "Ngày tạo", "Quyền Admin", "Password hash", "Status", "Date of Birth", "Gender"]
        rows = []
        
        for user in users:
            # Hiển thị quyền admin như Có/Không
            admin_status = "Có" if user.admin else "Không"

            
            rows.append([
                user.id,
                user.ho_ten,
                user.so_dien_thoai,
                user.diem_thuong,
                user.ngay_tao.strftime("%Y-%m-%d %H:%M:%S") if hasattr(user, 'ngay_tao') and user.ngay_tao else "N/A",
                admin_status,
                user.hashed_password,
                user.status,
                user.date_of_birth,
                user.gender
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH NGƯỜI DÙNG VÀ QUYỀN ADMIN ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số người dùng: {len(users)}")
        
        # Hiển thị riêng danh sách admin
        admin_users = [user for user in users if user.admin]
        if admin_users:
            print("\n=== DANH SÁCH NGƯỜI DÙNG CÓ QUYỀN ADMIN ===")
            admin_rows = []
            for admin in admin_users:
                admin_rows.append([
                    admin.id,
                    admin.ho_ten,
                    admin.so_dien_thoai
                ])
            print(tabulate(admin_rows, headers=["ID", "Họ Tên", "Số điện thoại"], tablefmt="pretty"))
            print(f"Tổng số admin: {len(admin_users)}")
        else:
            print("\nKhông có người dùng nào có quyền admin")
        
    finally:
        db.close()


def show_paint_types():
    db = SessionLocal()
    try:
        # Lấy tất cả paint types từ database
        paint_types = db.query(PaintType).all()
        
        if not paint_types:
            print("Không có dữ liệu loại sơn trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["ID", "Loại Sơn", "Mô tả sp", "Thành phần", "Hướng dẫn sử dụng", "Bảo quản", "Lưu ý"]
        rows = []
        
        for pt in paint_types:
            rows.append([
                pt.id,
                pt.paint_type,  
                pt.mo_ta_san_pham,
                pt.thanh_phan,
                pt.huong_dan_su_dung, 
                pt.bao_quan,
                pt.luu_y              
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH LOẠI SƠN ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số loại sơn: {len(paint_types)}")
        
    finally:
        db.close()


def show_image_resources():
    db = SessionLocal()
    try:
        # Lấy tất cả image resources từ database
        images = db.query(ImageResource).all()
        
        if not images:
            print("Không có dữ liệu tài nguyên hình ảnh trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["ID", "Đường dẫn hình ảnh"]
        rows = []
        
        for img in images:
            # Rút gọn UUID để dễ đọc
            rows.append([
                img.id,
                img.image_path
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH TÀI NGUYÊN HÌNH ẢNH ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số tài nguyên hình ảnh: {len(images)}")
        
    finally:
        db.close()

def show_type_details():
    db = SessionLocal()
    try:
        # Lấy tất cả type details từ database với thông tin paint type
        type_details = db.query(TypeDetail).options(joinedload(TypeDetail.paint_type)).all()
        
        if not type_details:
            print("Không có dữ liệu chi tiết loại sơn trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["ID", "ID PT", "Loại Sơn", "Sản Phẩm", "Mã", "Đóng Gói", "Thể tích", "Giá", "Phủ (m²)", "Khuyến Mãi" ,"is active", "Tính năng"]
        rows = []
        
        for detail in type_details:
            rows.append([
                detail.id,
                detail.paint_type.id,
                detail.paint_type.paint_type if detail.paint_type else "N/A",
                detail.product,
                detail.code,
                detail.package,
                f"{detail.volume:.1f}" if detail.volume else "N/A",
                f"{detail.price:,.0f} VNĐ" if detail.price else "N/A",
                f"{detail.m2_cover:.1f}" if detail.m2_cover else "N/A",
                detail.promotion or "Không có",
                detail.is_active,
                detail.features
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH CHI TIẾT SẢN PHẨM SƠN ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số sản phẩm: {len(type_details)}")
        
        # Hiển thị số lượng sản phẩm theo loại sơn
        print("\n=== THỐNG KÊ THEO LOẠI SƠN ===")
        paint_type_stats = (
            db.query(PaintType.paint_type, func.count(TypeDetail.id))
            .outerjoin(TypeDetail, PaintType.id == TypeDetail.paint_type_id)
            .group_by(PaintType.paint_type)
            .all()
        )
        
        stat_headers = ["Loại Sơn", "Số Lượng Sản Phẩm"]
        stat_rows = []
        
        for paint_type, count in paint_type_stats:
            stat_rows.append([paint_type, count])
            
        print(tabulate(stat_rows, headers=stat_headers, tablefmt="pretty"))
        
    finally:
        db.close()



def show_token_store():
    db = SessionLocal()
    try:
        # Lấy tất cả tokens từ database với thông tin user
        tokens = db.query(TokenStore).options(joinedload(TokenStore.user)).all()
        
        if not tokens:
            print("Không có dữ liệu token trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["ID", "User ID", "Họ tên", "Token (rút gọn)", "Hết hạn", "Thu hồi", "Thiết bị", "Tạo lúc", "Sử dụng lần cuối"]
        rows = []
        
        now = datetime.utcnow()
        
        for token in tokens:
            # Hiển thị token dạng rút gọn để dễ đọc
            short_token = f"{token.token[:8]}...{token.token[-8:]}" if token.token else "N/A"
            
            # Tính trạng thái hiện tại của token
            is_expired = "Hết hạn" if token.expires_at < now else "Còn hạn"
            is_revoked = "Đã thu hồi" if token.is_revoked else "Còn hiệu lực"
            status = f"{is_revoked}, {is_expired}"
            
            rows.append([
                token.id,
                token.user_id,
                token.user.ho_ten if token.user else "N/A",
                short_token,
                token.expires_at.strftime("%Y-%m-%d %H:%M"),
                status,
                token.device_info[:30] + "..." if token.device_info and len(token.device_info) > 30 else token.device_info,
                token.created_at.strftime("%Y-%m-%d %H:%M"),
                token.last_used_at.strftime("%Y-%m-%d %H:%M")
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH TOKEN ĐĂNG NHẬP GHI NHỚ ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số token: {len(tokens)}")
        
        # Hiển thị thống kê
        valid_tokens = sum(1 for t in tokens if not t.is_revoked and t.expires_at > now)
        revoked_tokens = sum(1 for t in tokens if t.is_revoked)
        expired_tokens = sum(1 for t in tokens if t.expires_at < now and not t.is_revoked)
        
        print(f"\nThống kê:")
        print(f"- Token hợp lệ: {valid_tokens}")
        print(f"- Token đã thu hồi: {revoked_tokens}")
        print(f"- Token đã hết hạn: {expired_tokens}")
        
    finally:
        db.close()

def show_product_images():
    db = SessionLocal()
    try:
        # Lấy tất cả sản phẩm với ảnh
        products = db.query(TypeDetail).options(joinedload(TypeDetail.images)).all()
        
        if not products:
            print("Không có sản phẩm trong database.")
            return
        
        # Hiển thị thống kê
        total_images = sum(len(product.images) for product in products)
        products_with_images = sum(1 for product in products if product.images)
        
        print(f"\n=== THỐNG KÊ ẢNH SẢN PHẨM ===")
        print(f"Tổng số sản phẩm: {len(products)}")
        print(f"Sản phẩm có ảnh: {products_with_images}")
        print(f"Tổng số ảnh: {total_images}")
        print(f"Trung bình: {total_images / len(products):.1f} ảnh/sản phẩm")
        
        # Hiển thị danh sách tất cả các sản phẩm
        headers = ["ID", "Sản phẩm", "Mã", "Số lượng ảnh"]
        rows = []
        
        for product in products:
            rows.append([
                product.id,
                product.product,
                product.code,
                len(product.images)
            ])
        
        print("\n=== DANH SÁCH SẢN PHẨM VÀ SỐ LƯỢNG ẢNH ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        
        # Hỏi người dùng có muốn xem chi tiết từng sản phẩm không
        show_details = input("\nBạn có muốn xem chi tiết ảnh của từng sản phẩm không? (y/n): ")
        
        if show_details.lower() == 'y':
            for product in products:
                if not product.images:
                    continue
                    
                print(f"\n=== ẢNH CỦA SẢN PHẨM: {product.product} (ID: {product.id}) ===")
                
                image_headers = ["ID", "Đường dẫn ảnh"]
                image_rows = []
                
                for image in product.images:
                    image_rows.append([
                        image.id,
                        image.image_path
                    ])
                
                print(tabulate(image_rows, headers=image_headers, tablefmt="pretty"))
        
    finally:
        db.close()

def show_product_thumbnail():
    db = SessionLocal()
    try:
        # Lấy tất cả sản phẩm với thumbnails
        products = db.query(TypeDetail).options(joinedload(TypeDetail.thumbnails)).all()
        
        if not products:
            print("Không có sản phẩm trong database.")
            return
        
        # Hiển thị thống kê
        total_thumbnails = sum(len(product.thumbnails) for product in products)
        products_with_thumbnails = sum(1 for product in products if product.thumbnails)
        
        print(f"\n=== THỐNG KÊ ẢNH THUMBNAIL SẢN PHẨM ===")
        print(f"Tổng số sản phẩm: {len(products)}")
        print(f"Sản phẩm có thumbnail: {products_with_thumbnails}")
        print(f"Tổng số thumbnail: {total_thumbnails}")
        print(f"Trung bình: {total_thumbnails / len(products):.1f} thumbnail/sản phẩm")
        
        # Hiển thị danh sách tất cả các sản phẩm
        headers = ["ID", "Sản phẩm", "Mã", "Số lượng thumbnail"]
        rows = []
        
        for product in products:
            rows.append([
                product.id,
                product.product,
                product.code,
                len(product.thumbnails)
            ])
        
        print("\n=== DANH SÁCH SẢN PHẨM VÀ SỐ LƯỢNG THUMBNAIL ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        
        # Hỏi người dùng có muốn xem chi tiết từng sản phẩm không
        show_details = input("\nBạn có muốn xem chi tiết thumbnail của từng sản phẩm không? (y/n): ")
        
        if show_details.lower() == 'y':
            for product in products:
                if not product.thumbnails:
                    continue
                    
                print(f"\n=== THUMBNAIL CỦA SẢN PHẨM: {product.product} (ID: {product.id}) ===")
                
                thumbnail_headers = ["ID", "Đường dẫn thumbnail"]
                thumbnail_rows = []
                
                for thumbnail in product.thumbnails:
                    thumbnail_rows.append([
                        thumbnail.id,
                        thumbnail.path_to_thumbnail
                    ])
                
                print(tabulate(thumbnail_rows, headers=thumbnail_headers, tablefmt="pretty"))
        
    finally:
        db.close()

def show_cart_database():
    """
    Hiển thị thông tin về giỏ hàng trong cơ sở dữ liệu
    """
    db = SessionLocal()
    try:
        # Lấy tất cả giỏ hàng với các item
        carts = db.query(Cart).filter(Cart.is_active == True).options(
            joinedload(Cart.cart_items).joinedload(CartItem.type_detail)
        ).all()
        
        if not carts:
            print("Không có giỏ hàng nào trong database.")
            return
        
        # Lấy danh sách tất cả người dùng có giỏ hàng
        users_with_carts = db.query(User).join(Cart).filter(Cart.is_active == True).all()
        
        # Hiển thị thống kê
        total_items = sum(len(cart.cart_items) for cart in carts)
        active_items = sum(sum(1 for item in cart.cart_items if item.is_active) for cart in carts)
        
        print(f"\n=== THỐNG KÊ GIỎ HÀNG ===")
        print(f"Tổng số giỏ hàng: {len(carts)}")
        print(f"Số người dùng có giỏ hàng: {len(users_with_carts)}")
        print(f"Tổng số sản phẩm trong giỏ hàng: {total_items}")
        print(f"Sản phẩm đang hoạt động: {active_items}")
        print(f"Trung bình: {active_items / len(carts):.1f} sản phẩm/giỏ hàng")
        
        # Hiển thị danh sách giỏ hàng
        headers = ["ID", "Người dùng", "Ngày tạo", "Số sản phẩm", "Tổng tiền"]
        rows = []
        
        for cart in carts:
            user = db.query(User).filter(User.id == cart.user_id).first()
            active_cart_items = [item for item in cart.cart_items if item.is_active]
            
            # Tính tổng tiền
            total_price = 0
            for item in active_cart_items:
                if item.type_detail and item.type_detail.price:
                    total_price += item.type_detail.price * item.quantity
            
            rows.append([
                cart.id,
                user.ho_ten if user else "Unknown",
                cart.created_at.strftime("%d/%m/%Y %H:%M") if cart.created_at else "N/A",
                len(active_cart_items),
                f"{total_price:,.0f} VND"
            ])
        
        print("\n=== DANH SÁCH GIỎ HÀNG ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        
        # Hỏi người dùng có muốn xem chi tiết từng giỏ hàng
        show_details = input("\nBạn có muốn xem chi tiết của từng giỏ hàng? (y/n): ")
        
        if show_details.lower() == 'y':
            for cart in carts:
                user = db.query(User).filter(User.id == cart.user_id).first()
                active_cart_items = [item for item in cart.cart_items]# if item.is_active]
                
                if not active_cart_items:
                    continue
                
                print(f"\n=== CHI TIẾT GIỎ HÀNG CỦA: {user.ho_ten if user else 'Unknown'} (ID: {cart.id}) ===")
                
                item_headers = ["ID", "Sản phẩm", "Mã màu", "Dung tích", "Số lượng", "Đơn giá", "Thành tiền", "is active"]
                item_rows = []
                
                for item in active_cart_items:
                    product_name = item.type_detail.product if item.type_detail else "Unknown"
                    price = item.type_detail.price if item.type_detail and item.type_detail.price else 0
                    total = price * item.quantity
                    
                    item_rows.append([
                        item.id,
                        product_name,
                        item.color_code,
                        f"{item.volume:.1f}L" if item.volume else "N/A",
                        item.quantity,
                        f"{price:,.0f} VND",
                        f"{total:,.0f} VND",
                        item.is_active
                    ])
                
                print(tabulate(item_rows, headers=item_headers, tablefmt="pretty"))

    finally:
        db.close()

if __name__ == "__main__":
    try:
        # show_users()
        # show_orders()
        # show_paint_types()
        # show_image_resources()
        # show_type_details()
        
        # show_order_details()
        # show_token_store()
        # show_product_images()
        # show_product_thumbnail()
        show_cart_database()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()