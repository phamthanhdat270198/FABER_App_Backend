import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def add_info_columns():
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
        
        # Kiểm tra xem các cột đã tồn tại chưa
        cursor.execute("PRAGMA table_info(paint_types)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Định nghĩa các cột cần thêm và thuộc tính của chúng
        new_columns = [
            {"name": "mo_ta_san_pham", "type": "TEXT", "nullable": False, "default": "''"},
            {"name": "thanh_phan", "type": "TEXT", "nullable": False, "default": "''"},
            {"name": "huong_dan_su_dung", "type": "TEXT", "nullable": False, "default": "''"},
            {"name": "luu_y", "type": "TEXT", "nullable": True, "default": "NULL"},
            {"name": "bao_quan", "type": "TEXT", "nullable": False, "default": "''"}
        ]
        
        # Thêm từng cột mới nếu chưa tồn tại
        columns_added = 0
        for col in new_columns:
            if col["name"] not in column_names:
                default_clause = f"DEFAULT {col['default']}" if col["default"] else ""
                nullable_clause = "NOT NULL" if not col["nullable"] else ""
                
                # Thêm cột mới
                sql = f"ALTER TABLE paint_types ADD COLUMN {col['name']} {col['type']} {nullable_clause} {default_clause}"
                cursor.execute(sql)
                columns_added += 1
                print(f"Đã thêm cột {col['name']} vào bảng paint_types.")
            else:
                print(f"Cột {col['name']} đã tồn tại trong bảng paint_types.")
        
        conn.commit()
        print(f"Đã thêm {columns_added} cột mới vào bảng paint_types.")
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    add_info_columns()