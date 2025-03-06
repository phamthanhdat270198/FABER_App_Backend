import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def change_uuid_to_id():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem bảng image_resources đã tồn tại chưa
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_resources'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # Nếu bảng chưa tồn tại, tạo mới luôn với cấu trúc ID
            cursor.execute('''
                CREATE TABLE image_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL
                )
            ''')
            conn.commit()
            print("Đã tạo bảng image_resources mới với khóa chính là ID")
        else:
            # Kiểm tra cấu trúc bảng hiện tại
            cursor.execute("PRAGMA table_info(image_resources)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'uuid' in column_names and 'id' not in column_names:
                # Tạo bảng tạm với cấu trúc mới
                cursor.execute('''
                    CREATE TABLE image_resources_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_path TEXT NOT NULL
                    )
                ''')
                
                # Sao chép dữ liệu từ bảng cũ sang bảng mới (bỏ qua cột uuid)
                cursor.execute('''
                    INSERT INTO image_resources_new (image_path)
                    SELECT image_path FROM image_resources
                ''')
                
                # Xóa bảng cũ
                cursor.execute("DROP TABLE image_resources")
                
                # Đổi tên bảng mới thành tên bảng cũ
                cursor.execute("ALTER TABLE image_resources_new RENAME TO image_resources")
                
                # Tạo index cho cột id
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_image_resources_id ON image_resources(id)")
                
                conn.commit()
                print("Đã thay đổi cấu trúc bảng image_resources từ UUID sang ID")
            elif 'id' in column_names:
                print("Bảng image_resources đã có cột ID làm khóa chính")
            else:
                print("Cấu trúc bảng image_resources không như dự kiến, vui lòng kiểm tra lại")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thay đổi cấu trúc bảng: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    change_uuid_to_id()