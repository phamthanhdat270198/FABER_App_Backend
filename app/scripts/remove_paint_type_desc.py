import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def remove_description_column():
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
        
        # Kiểm tra xem cột description có tồn tại không
        cursor.execute("PRAGMA table_info(paint_types)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'description' not in column_names:
            print("Cột description không tồn tại trong bảng paint_types.")
            return
        
        # SQLite không hỗ trợ trực tiếp việc xóa cột
        # Cần tạo bảng mới và sao chép dữ liệu
        
        # 1. Lấy tất cả các cột trừ cột description
        other_columns = [col for col in column_names if col != 'description']
        columns_str = ', '.join(other_columns)
        
        # 2. Tạo bảng tạm thời
        cursor.execute(f"CREATE TABLE paint_types_new ({', '.join([f'{col} {columns[i][2]}' for i, col in enumerate(column_names) if col != 'description'])})")
        
        # 3. Sao chép dữ liệu từ bảng cũ sang bảng mới
        cursor.execute(f"INSERT INTO paint_types_new SELECT {columns_str} FROM paint_types")
        
        # 4. Xóa bảng cũ
        cursor.execute("DROP TABLE paint_types")
        
        # 5. Đổi tên bảng mới thành tên bảng cũ
        cursor.execute("ALTER TABLE paint_types_new RENAME TO paint_types")
        
        # 6. Tạo lại các indexes nếu cần
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paint_types_id ON paint_types(id)")
        
        conn.commit()
        print("Đã xóa cột description khỏi bảng paint_types thành công!")
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi xóa cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    remove_description_column()