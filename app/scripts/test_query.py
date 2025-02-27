# app/scripts/query_relationships.py
import os
import sys
from tabulate import tabulate
from sqlalchemy import desc, func

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
root_dir = os.path.dirname(app_dir)
sys.path.append(root_dir)

from app.db.base import SessionLocal
from app.models.user import User
from app.models.order import Order, OrderStatus
from sqlalchemy.orm import joinedload

def run_relationship_queries():
    db = SessionLocal()
    try:
        print("\n===== CÁC CÂU QUERY THỂ HIỆN MỐI QUAN HỆ USER-ORDER =====\n")
        
        # 1. Lấy tất cả order của một user cụ thể
        print("1. Tất cả các đơn hàng của user có ID=1:")
        user = db.query(User).filter(User.id == 1).first()
        if user:
            print(f"User: {user.ho_ten} (ID: {user.id})")
            
            headers = ["Order ID", "Ngày tạo", "Trạng thái"]
            rows = []
            for order in user.orders:
                rows.append([order.id, order.date_time, order.status.value])
            
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print("Không tìm thấy user có ID=1")
        
        # 2. Join hai bảng và lấy thông tin kết hợp
        print("\n2. Join User và Order để lấy thông tin kết hợp:")
        joined_data = (
            db.query(Order.id, User.ho_ten, User.so_dien_thoai, Order.date_time, Order.status)
            .join(User, User.id == Order.user_id)
            .filter(Order.is_deleted == False)
            .order_by(desc(Order.date_time))
            .all()
        )
        
        if joined_data:
            headers = ["Order ID", "Họ tên KH", "SĐT", "Ngày tạo", "Trạng thái"]
            rows = []
            for order_id, ho_ten, so_dien_thoai, date_time, status in joined_data:
                rows.append([order_id, ho_ten, so_dien_thoai, date_time, status.value])
            
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print("Không có dữ liệu kết hợp")
        
        # 3. Đếm số lượng đơn hàng theo người dùng
        print("\n3. Số lượng đơn hàng của mỗi người dùng:")
        user_order_counts = (
            db.query(User.id, User.ho_ten, func.count(Order.id).label("order_count"))
            .outerjoin(Order, User.id == Order.user_id)
            .group_by(User.id, User.ho_ten)
            .order_by(desc("order_count"))
            .all()
        )
        
        if user_order_counts:
            headers = ["User ID", "Họ tên", "Số lượng đơn hàng"]
            rows = []
            for user_id, ho_ten, order_count in user_order_counts:
                rows.append([user_id, ho_ten, order_count])
                
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print("Không có dữ liệu")
        
        # 4. Eager loading: Lấy tất cả users kèm order của họ
        print("\n4. Eager loading - Lấy users kèm orders:")
        users_with_orders = db.query(User).options(joinedload(User.orders)).all()
        
        for user in users_with_orders:
            print(f"\nUser: {user.ho_ten} (ID: {user.id})")
            if user.orders:
                headers = ["Order ID", "Ngày tạo", "Trạng thái"]
                rows = []
                for order in user.orders:
                    rows.append([order.id, order.date_time, order.status.value])
                
                print(tabulate(rows, headers=headers, tablefmt="pretty"))
            else:
                print("  Không có đơn hàng")
        
        # 5. Lọc người dùng theo trạng thái đơn hàng
        print("\n5. Danh sách người dùng có ít nhất một đơn hàng đang PENDING:")
        users_with_pending = (
            db.query(User)
            .join(Order, User.id == Order.user_id)
            .filter(Order.status == OrderStatus.PENDING)
            .distinct()
            .all()
        )
        
        if users_with_pending:
            headers = ["User ID", "Họ tên"]
            rows = []
            for user in users_with_pending:
                rows.append([user.id, user.ho_ten])
                
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
        else:
            print("Không có người dùng nào có đơn hàng đang PENDING")
        
    finally:
        db.close()

if __name__ == "__main__":
    try:
        run_relationship_queries()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()