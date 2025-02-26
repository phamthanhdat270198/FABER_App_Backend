# app/scripts/show_data.py
import os
import sys
from tabulate import tabulate  # Cài đặt với: pip install tabulate

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(app_dir)
sys.path.append(root_dir)

from app.db.base import SessionLocal
from app.models.user import User

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

if __name__ == "__main__":
    try:
        show_users()
    except Exception as e:
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()