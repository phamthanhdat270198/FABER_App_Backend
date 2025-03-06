import os
import sys
from tabulate import tabulate  # Cài đặt với: pip install tabulate

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
print("current dir = ", current_dir)
app_dir = os.path.dirname(current_dir)
print("app dir = ", app_dir)
root_dir = os.path.dirname(app_dir)
print("root dir == ", root_dir)
sys.path.append(root_dir)

from app.db.base import SessionLocal
from app.models.order import Order
from app.models.user import User
from app.models.paint_type import PaintType
from app.models.image_resource import ImageResource
from app.models.type_detail import TypeDetail
from app.models.order_detail import OrderDetail 

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
        headers = ["ID", "Họ Tên", "Số điện thoại", "Điểm thưởng", "Ngày tạo", "Quyền Admin", "Password hash"]
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
                user.status
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

def show_orders():
    db = SessionLocal()
    try:
        # Lấy tất cả orders từ database với thông tin user
        orders = db.query(Order).options(joinedload(Order.user)).all()
        
        if not orders:
            print("Không có dữ liệu đơn hàng trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["Order ID", "User ID", "Họ Tên User", "Ngày Tạo", "Trạng Thái", "Đã Xóa"]
        rows = []
        
        for order in orders:
            rows.append([
                order.id,
                order.user_id,
                order.user.ho_ten if order.user else "N/A",
                order.date_time.strftime("%Y-%m-%d %H:%M:%S"),
                order.status.value,
                "Có" if order.is_deleted else "Không"
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH ĐƠN HÀNG ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số đơn hàng: {len(orders)}")
        
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
        headers = ["ID", "Loại Sơn", "Mô tả"]
        rows = []
        
        for pt in paint_types:
            rows.append([
                pt.id,
                pt.paint_type,
                pt.description
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
        headers = ["ID", "Loại Sơn", "Sản Phẩm", "Mã", "Đóng Gói", "Thể tích", "Giá", "Phủ (m²)", "Khuyến Mãi"]
        rows = []
        
        for detail in type_details:
            rows.append([
                detail.id,
                detail.paint_type.paint_type if detail.paint_type else "N/A",
                detail.product,
                detail.code,
                detail.package,
                f"{detail.volume:.1f}" if detail.volume else "N/A",
                f"{detail.price:,.0f} VNĐ" if detail.price else "N/A",
                f"{detail.m2_cover:.1f}" if detail.m2_cover else "N/A",
                detail.promotion or "Không có"
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

def show_order_details():
    db = SessionLocal()
    try:
        # Lấy tất cả order details từ database với các thông tin liên quan
        order_details = (
            db.query(OrderDetail)
            .options(
                joinedload(OrderDetail.order).joinedload(Order.user),
                joinedload(OrderDetail.type_detail).joinedload(TypeDetail.paint_type)
            )
            .all()
        )
        
        if not order_details:
            print("Không có dữ liệu chi tiết đơn hàng trong database.")
            return
        
        # Chuẩn bị dữ liệu cho bảng
        headers = ["ID", "Đơn Hàng", "Khách Hàng", "Sản Phẩm", "Số Lượng", "Đơn Giá", "Thành Tiền"]
        rows = []
        
        for detail in order_details:
            # Lấy thông tin từ các bảng liên kết
            order_id = detail.order.id if detail.order else "N/A"
            customer_name = detail.order.user.ho_ten if detail.order and detail.order.user else "N/A"
            product_name = detail.type_detail.product if detail.type_detail else "N/A"
            unit_price = detail.type_detail.price if detail.type_detail else 0
            
            rows.append([
                detail.id,
                f"#{order_id}",
                customer_name,
                product_name,
                detail.quantity,
                f"{unit_price:,.0f} VNĐ" if unit_price else "N/A",
                f"{detail.total_amount:,.0f} VNĐ"
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== CHI TIẾT ĐƠN HÀNG ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số mục: {len(order_details)}")
        
        # Hiển thị tổng tiền theo đơn hàng
        print("\n=== TỔNG TIỀN THEO ĐƠN HÀNG ===")
        order_totals = (
            db.query(
                Order.id,
                User.ho_ten,
                Order.date_time,
                Order.status,
                func.sum(OrderDetail.total_amount).label("total")
            )
            .join(OrderDetail, Order.id == OrderDetail.order_id)
            .join(User, Order.user_id == User.id)
            .group_by(Order.id, User.ho_ten, Order.date_time, Order.status)
            .all()
        )
        
        if order_totals:
            total_headers = ["Đơn Hàng", "Khách Hàng", "Ngày Tạo", "Trạng Thái", "Tổng Tiền"]
            total_rows = []
            
            for order_id, customer_name, date_time, status, total in order_totals:
                total_rows.append([
                    f"#{order_id}",
                    customer_name,
                    date_time.strftime("%Y-%m-%d %H:%M"),
                    status.value,
                    f"{total:,.0f} VNĐ"
                ])
                
            print(tabulate(total_rows, headers=total_headers, tablefmt="pretty"))
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # show_users()
        # show_orders()
        # show_paint_types()
        show_image_resources()
        # show_type_details()
        # show_order_details()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()