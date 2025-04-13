import os
import sys
import sqlite3
from datetime import datetime

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("curent = ", current_dir)
root_dir = os.path.dirname(current_dir)
print("root dir = ", root_dir)
sys.path.append(root_dir)

# Đường dẫn đến file database
DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def add_created_date_column():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem cột đã tồn tại chưa
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'ngay_tao' not in column_names:
            # SQLite không hỗ trợ ALTER TABLE ADD COLUMN với NOT NULL và DEFAULT 
            # nên chúng ta cần tạo một bảng tạm thời, sao chép dữ liệu và đổi tên
            
            # 1. Tạo bảng tạm thời với cột mới
            cursor.execute('''
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ho_ten TEXT NOT NULL,
                    dia_chi TEXT,
                    so_dien_thoai TEXT,
                    diem_thuong REAL DEFAULT 0.0,
                    ngay_tao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. Sao chép dữ liệu từ bảng cũ sang bảng mới
            cursor.execute('''
                INSERT INTO users_new (id, ho_ten, dia_chi, so_dien_thoai, diem_thuong, ngay_tao)
                SELECT id, ho_ten, dia_chi, so_dien_thoai, diem_thuong, CURRENT_TIMESTAMP
                FROM users
            ''')
            
            # 3. Xóa bảng cũ
            cursor.execute("DROP TABLE users")
            
            # 4. Đổi tên bảng mới thành tên bảng cũ
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            # 5. Tạo lại các indexes (nếu có)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_id ON users(id)")
            
            conn.commit()
            print("Đã thêm cột ngày tạo (ngay_tao) vào bảng users thành công!")
        else:
            print("Cột ngay_tao đã tồn tại trong bảng users")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def add_admin_column():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem cột đã tồn tại chưa
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'admin' not in column_names:
            # SQLite không hỗ trợ ALTER TABLE ADD COLUMN với NOT NULL và DEFAULT 
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
            create_table_sql = "CREATE TABLE users_new (\n"
            for col_name, col_info in columns_info.items():
                create_table_sql += f"    {col_name} {col_info['type']}"
                
                if col_info['pk']:
                    create_table_sql += " PRIMARY KEY"
                    
                if col_info['not_null']:
                    create_table_sql += " NOT NULL"
                    
                if col_info['default'] is not None:
                    create_table_sql += f" DEFAULT {col_info['default']}"
                    
                create_table_sql += ",\n"
                
            # Thêm cột admin
            create_table_sql += "    admin BOOLEAN NOT NULL DEFAULT 0\n"
            create_table_sql += ")"
            
            # 3. Tạo bảng mới
            cursor.execute(create_table_sql)
            
            # 4. Sao chép dữ liệu từ bảng cũ sang bảng mới
            columns_to_copy = ", ".join(column_names)
            cursor.execute(f"""
                INSERT INTO users_new ({columns_to_copy}, admin)
                SELECT {columns_to_copy}, 0
                FROM users
            """)
            
            # 5. Xóa bảng cũ
            cursor.execute("DROP TABLE users")
            
            # 6. Đổi tên bảng mới thành tên bảng cũ
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            # 7. Tạo lại các indexes (nếu có)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_id ON users(id)")
            
            conn.commit()
            print("Đã thêm cột admin vào bảng users thành công!")
            
            # 8. Cập nhật quyền admin cho user đầu tiên
            cursor.execute("UPDATE users SET admin = 1 WHERE id = 1")
            conn.commit()
            print("Đã cấp quyền admin cho người dùng có ID=1")
        else:
            print("Cột admin đã tồn tại trong bảng users")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
def add_password_field():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem các cột đã tồn tại chưa
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Kiểm tra xem số điện thoại đã có unique constraint chưa
        has_hashed_password = 'hashed_password' in column_names
        
        # Đầu tiên, đảm bảo số điện thoại là unique
        if 'so_dien_thoai' in column_names:
            # Lấy danh sách các indexes
            cursor.execute("PRAGMA index_list(users)")
            indexes = cursor.fetchall()
            
            # Kiểm tra xem đã có index cho so_dien_thoai chưa
            has_phone_index = any(idx[1].startswith('idx_users_so_dien_thoai') for idx in indexes)
            
            if not has_phone_index:
                # Thêm index và unique constraint cho so_dien_thoai
                try:
                    cursor.execute("CREATE UNIQUE INDEX idx_users_so_dien_thoai ON users(so_dien_thoai)")
                    conn.commit()
                    print("Đã thêm UNIQUE constraint cho cột so_dien_thoai")
                except sqlite3.OperationalError as e:
                    # Nếu có lỗi duplicate values
                    if "UNIQUE constraint failed" in str(e):
                        print("Không thể tạo UNIQUE constraint vì có giá trị trùng lặp trong so_dien_thoai")
                    else:
                        raise
        
        # Thêm cột hashed_password nếu chưa có
        if not has_hashed_password:
            cursor.execute("ALTER TABLE users ADD COLUMN hashed_password TEXT")
            conn.commit()
            print("Đã thêm cột hashed_password vào bảng users")
        
        # Thêm mật khẩu mặc định cho admin nếu chưa có
        cursor.execute("SELECT id, so_dien_thoai, hashed_password FROM users WHERE admin = 1")
        admin_users = cursor.fetchall()
        
        if admin_users:
            from app.core.security import get_password_hash
            default_password = get_password_hash("admin123")
            
            for admin_id, phone, current_pwd in admin_users:
                if not current_pwd:  # Nếu chưa có mật khẩu
                    if not phone:  # Nếu chưa có số điện thoại
                        # Cập nhật cả số điện thoại và mật khẩu
                        cursor.execute(
                            "UPDATE users SET so_dien_thoai = ?, hashed_password = ? WHERE id = ?", 
                            (f"admin{admin_id}", default_password, admin_id)
                        )
                    else:
                        # Chỉ cập nhật mật khẩu
                        cursor.execute(
                            "UPDATE users SET hashed_password = ? WHERE id = ?", 
                            (default_password, admin_id)
                        )
            
            conn.commit()
            print("Đã cập nhật mật khẩu mặc định cho các tài khoản admin")
            print("Thông tin đăng nhập admin:")
            
            # Hiển thị thông tin các tài khoản admin
            cursor.execute("SELECT id, so_dien_thoai FROM users WHERE admin = 1")
            for admin_id, phone in cursor.fetchall():
                print(f"  - Admin ID={admin_id}, Số điện thoại: {phone}, Mật khẩu: admin123")
        
    except Exception as e:
        conn.rollback()
        print(f"Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def add_status_column():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Kiểm tra xem cột status đã tồn tại chưa
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'status' not in column_names:
            # SQLite không hỗ trợ ALTER TABLE ADD COLUMN với NOT NULL và DEFAULT cho enum
            # nên chúng ta cần tạo một bảng tạm thời, sao chép dữ liệu và đổi tên
            
            # 1. Tạo bảng tạm thời với cột mới
            cursor.execute('''
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ho_ten TEXT NOT NULL,
                    dia_chi TEXT,
                    so_dien_thoai TEXT NOT NULL,
                    diem_thuong REAL DEFAULT 0.0,
                    ngay_tao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    admin BOOLEAN NOT NULL DEFAULT 0,
                    hashed_password TEXT,
                    status TEXT NOT NULL DEFAULT 'PENDING'
                )
            ''')
            
            # 2. Sao chép dữ liệu từ bảng cũ sang bảng mới
            cursor.execute('''
                INSERT INTO users_new (id, ho_ten, dia_chi, so_dien_thoai, diem_thuong, ngay_tao, admin, hashed_password)
                SELECT id, ho_ten, dia_chi, so_dien_thoai, diem_thuong, ngay_tao, admin, hashed_password
                FROM users
            ''')
            
            # 3. Đặt tất cả tài khoản admin thành 'ACCEPTED' (viết hoa)
            cursor.execute('''
                UPDATE users_new SET status = 'ACCEPTED' WHERE admin = 1
            ''')
            
            # 4. Xóa bảng cũ
            cursor.execute("DROP TABLE users")
            
            # 5. Đổi tên bảng mới thành tên bảng cũ
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            # 6. Tạo lại các indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_id ON users(id)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_so_dien_thoai ON users(so_dien_thoai)")
            
            conn.commit()
            print("Đã thêm cột status vào bảng users thành công!")
            print("Tài khoản admin đã được đặt thành 'ACCEPTED'")
        else:
            # Nếu cột status đã tồn tại, kiểm tra xem có cần cập nhật giá trị không
            cursor.execute('''
                UPDATE users SET status = 'ACCEPTED' WHERE status = 'accepted'
            ''')
            cursor.execute('''
                UPDATE users SET status = 'PENDING' WHERE status = 'pending'
            ''')
            conn.commit()
            print("Đã cập nhật giá trị status sang chữ hoa")
    
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi thêm/cập nhật cột: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
def add_kth_spin_column():
    # Kiểm tra xem file database có tồn tại không
    if not os.path.exists(DATABASE_PATH):
        print(f"Không tìm thấy database tại: {DATABASE_PATH}")
        return
    
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    if 'kth_spin' not in column_names:
        # Thêm cột kth_spin vào bảng users với giá trị mặc định là 0
        cursor.execute("ALTER TABLE users ADD COLUMN kth_spin INTEGER DEFAULT 0")
        print("Đã thêm cột kth_spin vào bảng users")
    else:
        print("Cột kth_spin đã tồn tại trong bảng users")

if __name__ == "__main__":
    # add_created_date_column()
    # add_admin_column()
    # add_password_field()
    # add_status_column()
    add_kth_spin_column()