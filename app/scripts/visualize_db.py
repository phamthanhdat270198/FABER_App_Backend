# app/scripts/show_data.py
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
        headers = ["ID", "Họ Tên", "Địa chỉ", "Số điện thoại", "Điểm thưởng"]
        rows = []
        
        for user in users:
            rows.append([
                user.id,
                user.ho_ten,
                user.dia_chi,
                user.so_dien_thoai,
                user.diem_thuong
            ])
        
        # Hiển thị dữ liệu dưới dạng bảng
        print("\n=== DANH SÁCH NGƯỜI DÙNG ===")
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        print(f"Tổng số người dùng: {len(users)}")
        
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
        headers = ["UUID", "Đường dẫn hình ảnh"]
        rows = []
        
        for img in images:
            # Rút gọn UUID để dễ đọc
            short_uuid = img.uuid[:8] + "..." + img.uuid[-4:]
            rows.append([
                short_uuid,
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

if __name__ == "__main__":
    try:
        # show_users()
        # show_orders()
        # show_paint_types()
        # show_image_resources()
        show_type_details()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()