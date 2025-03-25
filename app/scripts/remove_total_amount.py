import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def modify_order_details_table():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Kiểm tra cấu trúc bảng hiện tại
        cursor.execute("PRAGMA table_info(order_details)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Kiểm tra xem cột đã tồn tại chưa
        has_total_amount = 'total_amount' in column_names
        has_color_code = 'color_code' in column_names
        
        if not has_total_amount and has_color_code:
            print("Bảng order_details đã được cập nhật trước đó.")
            return
        
        print("Bắt đầu cập nhật bảng order_details...")
        
        # 2. Tạo bảng mới với cấu trúc mới
        cursor.execute('''
            CREATE TABLE order_details_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                type_detail_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                color_code TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (type_detail_id) REFERENCES type_details(id)
            )
        ''')
        
        # 3. Sao chép dữ liệu từ bảng cũ sang bảng mới (loại bỏ total_amount)
        if has_total_amount:
            cursor.execute('''
                INSERT INTO order_details_new (id, order_id, type_detail_id, quantity)
                SELECT id, order_id, type_detail_id, quantity
                FROM order_details
            ''')
            print("Đã sao chép dữ liệu từ bảng cũ sang bảng mới.")
        
        # 4. Xóa bảng cũ
        cursor.execute("DROP TABLE order_details")
        print("Đã xóa bảng cũ.")
        
        # 5. Đổi tên bảng mới thành tên bảng cũ
        cursor.execute("ALTER TABLE order_details_new RENAME TO order_details")
        print("Đã đổi tên bảng mới thành order_details.")
        
        # 6. Tạo lại indexes (nếu cần)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_details_order_id ON order_details(order_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_details_type_detail_id ON order_details(type_detail_id)")
        print("Đã tạo lại các indexes.")
        
        conn.commit()
        print("Cập nhật bảng order_details hoàn tất!")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi cập nhật bảng: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    modify_order_details_table()