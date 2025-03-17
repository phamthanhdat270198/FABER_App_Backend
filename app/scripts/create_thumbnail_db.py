import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def create_thumbnail_table():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem bảng thumbnails đã tồn tại chưa
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thumbnails'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Tạo bảng thumbnails
            cursor.execute('''
                CREATE TABLE thumbnails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_detail_id INTEGER NOT NULL,
                    path_to_thumbnail TEXT NOT NULL,
                    FOREIGN KEY (type_detail_id) REFERENCES type_details(id) ON DELETE CASCADE
                )
            ''')
            
            # Tạo index cho type_detail_id
            cursor.execute("CREATE INDEX idx_thumbnails_type_detail_id ON thumbnails(type_detail_id)")
            
            conn.commit()
            print("Đã tạo bảng thumbnails thành công!")
        else:
            print("Bảng thumbnails đã tồn tại.")
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi tạo bảng: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    create_thumbnail_table()