import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def add_is_active_column():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem bảng paint_types có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paint_types'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Bảng paint_types không tồn tại trong database.")
            return
        
        # Kiểm tra xem cột is_active đã tồn tại chưa
        cursor.execute("PRAGMA table_info(paint_types)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_active' not in column_names:
            # Thêm cột is_active với giá trị mặc định là TRUE (1)
            cursor.execute("ALTER TABLE paint_types ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1")
            conn.commit()
            print("Đã thêm cột is_active vào bảng paint_types thành công!")
        else:
            print("Cột is_active đã tồn tại trong bảng paint_types.")
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    add_is_active_column()