import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def add_profile_columns():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem bảng users có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Bảng users không tồn tại trong database.")
            return
        
        # Kiểm tra xem các cột đã tồn tại chưa
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Thêm cột date_of_birth nếu chưa tồn tại
        if 'date_of_birth' not in column_names:
            cursor.execute("ALTER TABLE users ADD COLUMN date_of_birth DATE")
            print("Đã thêm cột date_of_birth vào bảng users.")
        else:
            print("Cột date_of_birth đã tồn tại trong bảng users.")
        
        # Thêm cột gender nếu chưa tồn tại
        if 'gender' not in column_names:
            cursor.execute("ALTER TABLE users ADD COLUMN gender TEXT")
            print("Đã thêm cột gender vào bảng users.")
        else:
            print("Cột gender đã tồn tại trong bảng users.")
        
        conn.commit()
        print("Quá trình thêm cột hoàn tất.")
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    add_profile_columns()