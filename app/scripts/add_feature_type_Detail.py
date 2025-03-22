import os
import sys
import sqlite3

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def add_features_column():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem cột features đã tồn tại chưa
        cursor.execute("PRAGMA table_info(type_details)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'features' not in column_names:
            # SQLite không hỗ trợ ALTER TABLE ADD COLUMN với một số ràng buộc
            # nên chúng ta cần tạo một bảng tạm thời, sao chép dữ liệu và đổi tên
            
            # 1. Kiểm tra cấu trúc bảng hiện tại
            columns_info = {}
            for col in columns:
                col_id, col_name, col_type, col_not_null, col_default, col_pk = col
                columns_info[col_name] = {
                    'type': col_type,
                    'not_null': col_not_null,
                    'default': col_default,
                    'pk': col_pk
                }
            
            # 2. Tạo câu lệnh SQL cho bảng mới
            create_table_sql = "CREATE TABLE type_details_new (\n"
            for col_name, col_info in columns_info.items():
                create_table_sql += f"    {col_name} {col_info['type']}"
                
                if col_info['pk']:
                    create_table_sql += " PRIMARY KEY"
                    
                if col_info['not_null']:
                    create_table_sql += " NOT NULL"
                    
                if col_info['default'] is not None:
                    create_table_sql += f" DEFAULT {col_info['default']}"
                    
                create_table_sql += ",\n"
                
            # Thêm cột features
            create_table_sql += "    features TEXT\n"
            create_table_sql += ")"
            
            # 3. Tạo bảng mới
            cursor.execute(create_table_sql)
            
            # 4. Sao chép dữ liệu từ bảng cũ sang bảng mới
            columns_to_copy = ", ".join(column_names)
            cursor.execute(f"""
                INSERT INTO type_details_new ({columns_to_copy}, features)
                SELECT {columns_to_copy}, NULL
                FROM type_details
            """)
            
            # 5. Xóa bảng cũ
            cursor.execute("DROP TABLE type_details")
            
            # 6. Đổi tên bảng mới thành tên bảng cũ
            cursor.execute("ALTER TABLE type_details_new RENAME TO type_details")
            
            # 7. Tạo lại các indexes (nếu có)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type_details_id ON type_details(id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type_details_paint_type_id ON type_details(paint_type_id)")
            
            conn.commit()
            print("Đã thêm cột features vào bảng type_details thành công!")
        else:
            print("Cột features đã tồn tại trong bảng type_details")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()



if __name__ == "__main__":
    add_features_column()