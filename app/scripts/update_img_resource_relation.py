import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def update_image_resource_relation():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem bảng image_resources có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_resources'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Kiểm tra cấu trúc bảng hiện tại
            cursor.execute("PRAGMA table_info(image_resources)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Kiểm tra xem cột type_detail_id đã tồn tại chưa
            has_relation = 'type_detail_id' in column_names
            
            if not has_relation:
                # Lưu trữ tạm dữ liệu hiện có
                cursor.execute("SELECT id, image_path FROM image_resources")
                existing_images = cursor.fetchall()
                
                # Tạo bảng mới với cấu trúc mới
                cursor.execute("DROP TABLE IF EXISTS image_resources_new")
                cursor.execute('''
                    CREATE TABLE image_resources_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        image_path TEXT NOT NULL,
                        type_detail_id INTEGER NOT NULL,
                        FOREIGN KEY (type_detail_id) REFERENCES type_details(id) ON DELETE CASCADE
                    )
                ''')
                
                # Kiểm tra xem có bảng type_details không
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='type_details'")
                type_details_exists = cursor.fetchone()
                
                if type_details_exists:
                    # Lấy ID sản phẩm đầu tiên để gán cho các ảnh hiện có
                    cursor.execute("SELECT id FROM type_details LIMIT 1")
                    first_product = cursor.fetchone()
                    
                    if first_product and existing_images:
                        default_type_detail_id = first_product[0]
                        
                        # Chuyển dữ liệu cũ sang bảng mới
                        for image_id, image_path in existing_images:
                            cursor.execute(
                                "INSERT INTO image_resources_new (id, image_path, type_detail_id) VALUES (?, ?, ?)",
                                (image_id, image_path, default_type_detail_id)
                            )
                        
                        print(f"Đã chuyển {len(existing_images)} ảnh sang sản phẩm có ID={default_type_detail_id}")
                    else:
                        # Nếu không có sản phẩm nào, thông báo để người dùng biết
                        print("Không có sản phẩm trong bảng type_details. Dữ liệu ảnh hiện tại sẽ không được chuyển đổi.")
                else:
                    print("Bảng type_details không tồn tại. Cần tạo bảng type_details trước.")
                
                # Xóa bảng cũ và đổi tên bảng mới
                cursor.execute("DROP TABLE image_resources")
                cursor.execute("ALTER TABLE image_resources_new RENAME TO image_resources")
                
                # Tạo index cho các trường quan trọng
                cursor.execute("CREATE INDEX idx_image_resources_type_detail_id ON image_resources(type_detail_id)")
                
                conn.commit()
                print("Đã cập nhật cấu trúc bảng image_resources thành công!")
            else:
                print("Bảng image_resources đã có quan hệ với type_details.")
        else:
            # Tạo bảng image_resources mới nếu chưa tồn tại
            cursor.execute('''
                CREATE TABLE image_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    type_detail_id INTEGER NOT NULL,
                    FOREIGN KEY (type_detail_id) REFERENCES type_details(id) ON DELETE CASCADE
                )
            ''')
            
            # Tạo index
            cursor.execute("CREATE INDEX idx_image_resources_type_detail_id ON image_resources(type_detail_id)")
            
            conn.commit()
            print("Đã tạo bảng image_resources mới thành công!")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi cập nhật bảng: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    update_image_resource_relation()