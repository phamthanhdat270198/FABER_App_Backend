import sqlite3
import os
import sys

def show_all_tables(db_path):
    """
    Hiển thị tên tất cả các bảng trong cơ sở dữ liệu SQLite
    
    Args:
        db_path (str): Đường dẫn đến file cơ sở dữ liệu SQLite
    """
    # Kiểm tra file database có tồn tại không
    if not os.path.exists(db_path):
        print(f"Lỗi: Database không tồn tại tại đường dẫn: {db_path}")
        return False
        
    try:
        # Kết nối tới database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Truy vấn lấy tên tất cả các bảng (không bao gồm bảng hệ thống SQLite)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        
        # Lấy kết quả
        tables = cursor.fetchall()
        
        # Hiển thị kết quả
        if tables:
            print(f"\n=== DANH SÁCH BẢNG TRONG DATABASE: {os.path.basename(db_path)} ===")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")
            print(f"\nTổng số bảng: {len(tables)}")
        else:
            print(f"Không tìm thấy bảng nào trong database {os.path.basename(db_path)}")
        
        # Đóng kết nối
        conn.close()
        
        return True
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        return False

import sqlite3
import os
import sys

def drop_order_tables(db_path="app.db"):
    """
    Xóa bảng orders và order_details từ cơ sở dữ liệu SQLite
    
    Args:
        db_path (str): Đường dẫn đến file cơ sở dữ liệu SQLite
    """
    # Kiểm tra file database có tồn tại không
    if not os.path.exists(db_path):
        print(f"Lỗi: Database không tồn tại tại đường dẫn: {db_path}")
        return False
        
    try:
        # Kết nối tới database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tắt tạm thời foreign key constraints để có thể xóa bảng an toàn
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Kiểm tra xem các bảng cần xóa có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('orders', 'order_details');")
        existing_tables = cursor.fetchall()
        existing_tables = [table[0] for table in existing_tables]
        
        if not existing_tables:
            print("Cả hai bảng 'orders' và 'order_details' đều không tồn tại trong database.")
            conn.close()
            return False
            
        # Hiển thị thông tin số bản ghi trong các bảng trước khi xóa
        print("\n=== THÔNG TIN TRƯỚC KHI XÓA ===")
        for table in existing_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"Bảng {table}: {count} bản ghi")
            
        # Xác nhận từ người dùng
        confirm = input("\nBạn có chắc chắn muốn xóa các bảng này? (y/n): ")
        if confirm.lower() != 'y':
            print("Đã hủy thao tác xóa bảng.")
            conn.close()
            return False
            
        # Xóa bảng order_details trước (nếu tồn tại) vì nó có thể có khóa ngoại tới orders
        if 'order_details' in existing_tables:
            cursor.execute("DROP TABLE order_details;")
            print("Đã xóa bảng 'order_details'")
            
        # Xóa bảng orders (nếu tồn tại)
        if 'orders' in existing_tables:
            cursor.execute("DROP TABLE orders;")
            print("Đã xóa bảng 'orders'")
            
        # Bật lại foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Lưu thay đổi
        conn.commit()
        
        # Xác nhận các bảng đã xóa
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('orders', 'order_details');")
        remaining_tables = cursor.fetchall()
        
        if not remaining_tables:
            print("\nĐã xóa thành công tất cả các bảng đã chọn.")
        else:
            print("\nCảnh báo: Một số bảng vẫn còn tồn tại:")
            for table in remaining_tables:
                print(f"- {table[0]}")
                
        # Đóng kết nối
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        return False
    
def clear_all_tables(db_path="app.db"):
    """
    Xóa tất cả dữ liệu trong các bảng nhưng giữ nguyên cấu trúc bảng
    
    Args:
        db_path (str): Đường dẫn đến file cơ sở dữ liệu SQLite
    """
    # Kiểm tra file database có tồn tại không
    if not os.path.exists(db_path):
        print(f"Lỗi: Database không tồn tại tại đường dẫn: {db_path}")
        return False
        
    try:
        # Kết nối tới database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lấy danh sách tất cả các bảng (không bao gồm bảng hệ thống SQLite)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        if not table_names:
            print("Không tìm thấy bảng nào trong database.")
            conn.close()
            return False
            
        # Tắt tạm thời foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Bắt đầu transaction
        conn.execute("BEGIN TRANSACTION;")
        
        # Hiển thị thông tin số bản ghi trong các bảng trước khi xóa
        print("\n=== THÔNG TIN TRƯỚC KHI XÓA DỮ LIỆU ===")
        table_counts = {}
        for table in table_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            table_counts[table] = count
            print(f"Bảng {table}: {count} bản ghi")
            
        # Xác nhận từ người dùng
        confirm = input("\nBạn có chắc chắn muốn xóa DỮ LIỆU từ TẤT CẢ các bảng? (y/n): ")
        if confirm.lower() != 'y':
            print("Đã hủy thao tác xóa dữ liệu.")
            conn.rollback()
            conn.close()
            return False
            
        # Xóa dữ liệu từ mỗi bảng
        for table in table_names:
            try:
                cursor.execute(f"DELETE FROM {table};")
                print(f"Đã xóa dữ liệu từ bảng '{table}'")
            except sqlite3.Error as e:
                print(f"Lỗi khi xóa dữ liệu từ bảng {table}: {e}")
                
        # Reset các auto-increment counters (SQLite sử dụng sqlite_sequence để lưu trữ này)
        cursor.execute("DELETE FROM sqlite_sequence;")
        print("Đã reset tất cả bộ đếm auto-increment")
        
        # Commit transaction
        conn.commit()
        
        # Bật lại foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Xác nhận việc xóa đã thành công
        print("\n=== THÔNG TIN SAU KHI XÓA DỮ LIỆU ===")
        for table in table_names:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"Bảng {table}: {count} bản ghi")
            
        print("\nĐã xóa thành công tất cả dữ liệu. Cấu trúc bảng vẫn được giữ nguyên.")
                
        # Đóng kết nối
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False

def seed_paint_types1(db_path="app.db"):
    """
    Thêm dữ liệu mẫu vào bảng paint_types
    
    Args:
        db_path (str): Đường dẫn đến file cơ sở dữ liệu SQLite
    """
    # Kiểm tra file database có tồn tại không
    if not os.path.exists(db_path):
        print(f"Lỗi: Database không tồn tại tại đường dẫn: {db_path}")
        return False
        
    try:
        # Kết nối tới database
        conn = sqlite3.connect(db_path)
        
        # Đảm bảo SQLite sử dụng foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        cursor = conn.cursor()
        
        # Kiểm tra xem bảng paint_types có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paint_types';")
        if not cursor.fetchone():
            print("Lỗi: Bảng 'paint_types' không tồn tại trong database.")
            conn.close()
            return False
        
        # Kiểm tra cấu trúc bảng (đảm bảo id là auto-increment)
        cursor.execute("PRAGMA table_info(paint_types);")
        columns = cursor.fetchall()
        pk_column = None
        for col in columns:
            if col[1] == 'id' and col[5] == 1:  # Tên cột là 'id' và là primary key
                pk_column = col
                break
                
        if not pk_column:
            print("Cảnh báo: Cột 'id' không được thiết lập đúng là PRIMARY KEY AUTOINCREMENT")
            confirm = input("Bạn có muốn tạo lại cấu trúc bảng paint_types đúng cách? (y/n): ")
            if confirm.lower() == 'y':
                # Tạo bảng tạm thời với cấu trúc đúng
                cursor.execute('''
                    CREATE TABLE paint_types_temp (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paint_type TEXT NOT NULL UNIQUE,
                        mo_ta_san_pham TEXT NOT NULL DEFAULT '',
                        thanh_phan TEXT NOT NULL DEFAULT '',
                        huong_dan_su_dung TEXT NOT NULL DEFAULT '',
                        luu_y TEXT,
                        bao_quan TEXT NOT NULL DEFAULT '',
                        is_active BOOLEAN NOT NULL DEFAULT 1
                    )
                ''')
                
                # Chuyển dữ liệu từ bảng cũ sang bảng tạm (nếu có dữ liệu)
                cursor.execute("SELECT COUNT(*) FROM paint_types;")
                if cursor.fetchone()[0] > 0:
                    cursor.execute('''
                        INSERT INTO paint_types_temp 
                            (paint_type, mo_ta_san_pham, thanh_phan, huong_dan_su_dung, luu_y, bao_quan, is_active)
                        SELECT 
                            paint_type, mo_ta_san_pham, thanh_phan, huong_dan_su_dung, luu_y, bao_quan, is_active
                        FROM paint_types
                    ''')
                
                # Xóa bảng cũ
                cursor.execute("DROP TABLE paint_types")
                
                # Đổi tên bảng tạm thành bảng chính
                cursor.execute("ALTER TABLE paint_types_temp RENAME TO paint_types")
                
                print("Đã tạo lại cấu trúc bảng paint_types với ID là AUTO INCREMENT")
            
        # Kiểm tra số lượng bản ghi hiện có
        cursor.execute("SELECT COUNT(*) FROM paint_types;")
        current_count = cursor.fetchone()[0]
        print(f"Hiện có {current_count} bản ghi trong bảng paint_types")
        
        # Danh sách các loại sơn mẫu
        paint_types_data = [
            {
                "paint_type": "Sơn mịn nội ngoại thất",
                "mo_ta_san_pham": "Sơn mịn nội ngoại thất cao cấp là sản phẩm sơn gốc acrylic, chuyên dùng làm lớp phủ hoàn thiện cuối cùng cho bề mặt bê tông, vữa thạch cao hoặc vữa xi măng. Sản phẩm giúp bề mặt tường phẳng, mịn màng, tăng độ bám dính cho lớp sơn phủ.",
                "thanh_phan": "Nhựa Acrylic\nCalcium Carbonate\nTalc\nChất tăng độ bám dính\nChất kháng nấm mốc\nPhụ gia chống kiềm",
                "huong_dan_su_dung": "Đảm bảo bề mặt tường sạch sẽ, khô, phẳng và độ ẩm dưới 16%\nKhuấy đều sơn trước khi sử dụng\nThi công bằng con lăn hoặc chổi quét. Số lớp thi công 2 lớp, mỗi lớp cách nhau tối thiểu 2 giờ\nPha loãng với nước sạch tỷ lệ 5-10% nếu cần thiết\nĐể khô hoàn toàn sau 24 giờ",
                "luu_y": "Không thi công khi nền nhiệt độ dưới 10°C hoặc trên 35°C\nThi công nhanh tay và đều lớp để tránh loang màu\nSử dụng ngay sau khi mở nắp bao bì",
                "bao_quan": "Để nơi khô ráo, thông thoáng, tránh ánh nắng trực tiếp\nXếp chồng bao bì không vượt quá 5 thùng chồng lên nhau\nSử dụng trong vòng 24 tháng tính từ ngày sản xuất",
                "is_active": True
            },
            {
                "paint_type": "Sơn bóng nội ngoại thất",
                "mo_ta_san_pham": "Sơn bóng là loại sơn phủ cao cấp với độ bóng cao, mang lại vẻ đẹp sang trọng cho bề mặt tường. Sản phẩm có khả năng chống bám bụi, dễ lau chùi và bền màu theo thời gian.",
                "thanh_phan": "Nhựa Acrylic cao cấp.\nChất tạo bóng.\nPhụ gia chống thấm.\nPhụ gia chống nấm mốc.\nPigment màu bền",
                "huong_dan_su_dung": "Làm sạch và làm phẳng bề mặt tường.\nKhuấy đều sơn trước khi sử dụng.\nThi công bằng con lăn hoặc súng phun. Nên sơn 2 lớp, mỗi lớp cách nhau ít nhất 2 giờ.\nCó thể pha loãng với nước sạch 5-10% nếu cần",
                "luu_y": None,
                "bao_quan": "Để nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp.\nĐậy kín nắp sau khi sử dụng.\nSử dụng trong vòng 24 tháng kể từ ngày sản xuất.",
                "is_active": True
            },
            {
                "paint_type": "Sơn chống thấm",
                "mo_ta_san_pham": "Sơn chống thấm là loại sơn gốc nước, có khả năng chống thấm tối ưu và mang lại lớp phủ màu sắc thẩm mỹ cho công trình. Sản phẩm thích hợp cho tường ngoài trời, sân thượng và các khu vực thường xuyên tiếp xúc với nước.",
                "thanh_phan": "Nhựa Acrylic chống thấm.\nChất tạo màu bền thời tiết.\nPhụ gia chống rêu mốc.\nChất chống kiềm hóa.",
                "huong_dan_su_dung": "Làm sạch và loại bỏ các lớp sơn cũ, bụi bẩn trên bề mặt.\nKhuấy đều sơn trước khi sử dụng.\nThi công 2 lớp, mỗi lớp cách nhau ít nhất 3 giờ.\nCó thể pha loãng với nước sạch 5-10% nếu cần.",
                "luu_y": None,
                "bao_quan": "Bảo quản nơi khô ráo, tránh ánh nắng trực tiếp.\nĐậy kín nắp sau khi sử dụng.\nDùng trong vòng 24 tháng từ ngày sản xuất.",
                "is_active": True
            },
            {
                "paint_type": "Sơn lót chống kiềm",
                "mo_ta_san_pham": "Sơn lót chống kiềm giúp ngăn ngừa hiện tượng kiềm hóa trên tường, tăng cường độ bám dính và kéo dài tuổi thọ cho lớp sơn phủ hoàn thiện. Sản phẩm phù hợp cho cả nội và ngoại thất.",
                "thanh_phan": "Nhựa Acrylic chống kiềm.\nPhụ gia chống nấm mốc.\nChất tăng độ bám dính.\nChất ổn định màu.",
                "huong_dan_su_dung": "Làm sạch bề mặt, loại bỏ bụi bẩn và tạp chất.\nKhuấy đều sơn trước khi sử dụng.\nThi công một lớp sơn lót, để khô hoàn toàn trước khi thi công lớp phủ.\nKhông cần pha loãng hoặc pha loãng nhẹ theo hướng dẫn nếu cần.",
                "luu_y": None,
                "bao_quan": "Để nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp.\nĐậy kín nắp sau khi sử dụng.\nSử dụng trong vòng 24 tháng kể từ ngày sản xuất.",
                "is_active": True
            },
            {
                "paint_type": "Sơn siêu bóng men sứ",
                "mo_ta_san_pham": "Sơn siêu bóng men sứ là loại sơn gốc nước cao cấp với bề mặt siêu bóng, mang lại vẻ đẹp sáng bóng như men sứ. Sản phẩm có khả năng chống thấm, chống bám bụi và dễ dàng lau chùi, thích hợp cho các bề mặt tường nội thất và ngoại thất cao cấp.",
                "thanh_phan": "Nhựa Acrylic cao cấp.\nChất tạo bóng đặc biệt.\nPhụ gia chống thấm.\nChất kháng nấm mốc, kháng kiềm.\nMàu sắc cao cấp chống phai.",
                "huong_dan_su_dung": "Chuẩn bị bề mặt sạch sẽ, phẳng và khô, độ ẩm dưới 16%.\nKhuấy đều sơn trước khi sử dụng.\nThi công bằng con lăn, chổi quét hoặc súng phun. Thi công 2 lớp, mỗi lớp cách nhau tối thiểu 2 giờ.\nCó thể pha loãng với 5-10% nước sạch nếu cần.\nĐể khô hoàn toàn sau 24 giờ để đạt độ bóng tối ưu.",
                "luu_y": "Không thi công khi nhiệt độ dưới 10°C hoặc trên 35°C.\nĐảm bảo sơn đều tay để đạt độ bóng cao và bề mặt mịn màng.\nSử dụng ngay sau khi mở nắp.",
                "bao_quan": "Để nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp.\nĐóng kín nắp sau khi sử dụng.\nSử dụng trong vòng 24 tháng kể từ ngày sản xuất.",
                "is_active": True
            }
        ]
        
        # Bắt đầu transaction để đảm bảo tính nhất quán dữ liệu
        conn.execute("BEGIN TRANSACTION;")
        
        # Thêm dữ liệu vào bảng paint_types
        added_count = 0
        for paint_type_data in paint_types_data:
            # Kiểm tra xem loại sơn đã tồn tại chưa
            cursor.execute("SELECT id FROM paint_types WHERE paint_type = ?", (paint_type_data["paint_type"],))
            existing = cursor.fetchone()
            
            if existing:
                print(f"Loại sơn '{paint_type_data['paint_type']}' đã tồn tại, bỏ qua.")
                continue
                
            # Thêm loại sơn mới
            cursor.execute('''
                INSERT INTO paint_types 
                (paint_type, mo_ta_san_pham, thanh_phan, huong_dan_su_dung, luu_y, bao_quan, is_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                paint_type_data["paint_type"],
                paint_type_data["mo_ta_san_pham"],
                paint_type_data["thanh_phan"],
                paint_type_data["huong_dan_su_dung"],
                paint_type_data["luu_y"],
                paint_type_data["bao_quan"],
                paint_type_data["is_active"]
            ))
            
            # Lấy ID vừa thêm
            new_id = cursor.lastrowid
            print(f"Đã thêm loại sơn: {paint_type_data['paint_type']} với ID: {new_id}")
            added_count += 1
        
        # Commit thay đổi sau khi thêm tất cả bản ghi
        conn.commit()
        
        # Kiểm tra số lượng bản ghi sau khi thêm
        cursor.execute("SELECT COUNT(*) FROM paint_types;")
        new_count = cursor.fetchone()[0]
        print(f"\nĐã thêm {added_count} loại sơn mới. Tổng số hiện tại: {new_count}")
        
        # Hiển thị danh sách các loại sơn
        cursor.execute("SELECT id, paint_type, is_active FROM paint_types;")
        paint_types = cursor.fetchall()
        
        print("\n=== DANH SÁCH LOẠI SƠN ===")
        for pt in paint_types:
            status = "Đang bán" if pt[2] else "Ngừng bán"
            print(f"ID: {pt[0]}, Loại sơn: {pt[1]}, Trạng thái: {status}")
        
        # Đóng kết nối
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False

def clear_paint_types(db_path="app.db"):
    """
    Xóa tất cả dữ liệu trong bảng paint_types nhưng giữ nguyên cấu trúc bảng
    
    Args:
        db_path (str): Đường dẫn đến file cơ sở dữ liệu SQLite
    """
    # Kiểm tra file database có tồn tại không
    if not os.path.exists(db_path):
        print(f"Lỗi: Database không tồn tại tại đường dẫn: {db_path}")
        return False
        
    try:
        # Kết nối tới database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Kiểm tra xem bảng paint_types có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paint_types';")
        if not cursor.fetchone():
            print("Lỗi: Bảng 'paint_types' không tồn tại trong database.")
            conn.close()
            return False
            
        # Kiểm tra số lượng bản ghi hiện có
        cursor.execute("SELECT COUNT(*) FROM paint_types;")
        current_count = cursor.fetchone()[0]
        print(f"Hiện có {current_count} bản ghi trong bảng paint_types")
        
        if current_count == 0:
            print("Bảng paint_types đã trống, không cần xóa dữ liệu.")
            conn.close()
            return True
            
        # Xác nhận từ người dùng
        confirm = input("\nBạn có chắc chắn muốn xóa TẤT CẢ dữ liệu từ bảng paint_types? (y/n): ")
        if confirm.lower() != 'y':
            print("Đã hủy thao tác xóa dữ liệu.")
            conn.close()
            return False
            
        # Tắt tạm thời foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Xóa dữ liệu từ bảng paint_types
        cursor.execute("DELETE FROM paint_types;")
        
        # Reset auto-increment counter cho bảng paint_types
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='paint_types';")
        
        # Hiển thị số bản ghi đã xóa
        print(f"Đã xóa {current_count} bản ghi từ bảng paint_types")
        
        # Kiểm tra xem có bảng liên quan không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='type_details';")
        if cursor.fetchone():
            # Kiểm tra số lượng bản ghi trong bảng type_details
            cursor.execute("SELECT COUNT(*) FROM type_details;")
            type_details_count = cursor.fetchone()[0]
            
            if type_details_count > 0:
                # Hỏi người dùng có muốn xóa dữ liệu từ bảng liên quan không
                confirm_related = input("\nBảng type_details có liên kết với paint_types và có dữ liệu. Bạn có muốn xóa dữ liệu trong bảng type_details không? (y/n): ")
                
                if confirm_related.lower() == 'y':
                    cursor.execute("DELETE FROM type_details;")
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='type_details';")
                    print(f"Đã xóa {type_details_count} bản ghi từ bảng type_details")
                else:
                    print("Giữ nguyên dữ liệu trong bảng type_details. Lưu ý: Có thể gây lỗi ràng buộc khóa ngoại khi thêm dữ liệu mới vào paint_types.")
        
        # Bật lại foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Commit thay đổi
        conn.commit()
        
        # Kiểm tra lại số lượng bản ghi sau khi xóa
        cursor.execute("SELECT COUNT(*) FROM paint_types;")
        after_count = cursor.fetchone()[0]
        
        print(f"\nKiểm tra sau khi xóa: {after_count} bản ghi trong bảng paint_types")
        print("Đã xóa thành công tất cả dữ liệu. Cấu trúc bảng paint_types vẫn được giữ nguyên.")
        
        # Đóng kết nối
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False

def clear_type_details_with_sqlite(db_path="app.db"):
    """
    Xóa tất cả dữ liệu trong bảng type_details sử dụng SQLite trực tiếp
    
    Args:
        db_path (str): Đường dẫn đến file database SQLite
    """
    # Kiểm tra file database có tồn tại không
    if not os.path.exists(db_path):
        print(f"Lỗi: Database không tồn tại tại đường dẫn: {db_path}")
        return False
        
    try:
        # Kết nối tới database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Kiểm tra xem bảng type_details có tồn tại không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='type_details';")
        if not cursor.fetchone():
            print("Bảng 'type_details' không tồn tại trong database.")
            conn.close()
            return False
            
        # Kiểm tra số lượng bản ghi hiện có
        cursor.execute("SELECT COUNT(*) FROM type_details;")
        current_count = cursor.fetchone()[0]
        print(f"Hiện có {current_count} bản ghi trong bảng type_details")
        
        if current_count == 0:
            print("Bảng type_details đã trống, không cần xóa dữ liệu.")
            conn.close()
            return True
        
        # Xác nhận từ người dùng
        confirm = input("\nBạn có chắc chắn muốn xóa TẤT CẢ dữ liệu từ bảng type_details? (y/n): ")
        if confirm.lower() != 'y':
            print("Đã hủy thao tác xóa dữ liệu.")
            conn.close()
            return False
            
        # Tắt tạm thời foreign key constraints
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Bắt đầu transaction
        conn.execute("BEGIN TRANSACTION;")
        
        # Kiểm tra xem có bảng images liên quan không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='image_resources';")
        has_images = cursor.fetchone()
        
        # Kiểm tra xem có bảng thumbnails liên quan không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thumbnails';")
        has_thumbnails = cursor.fetchone()
        
        # Kiểm tra xem có bảng cart_items liên quan không
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cart_items';")
        has_cart_items = cursor.fetchone()
        
        # Xóa dữ liệu từ bảng liên quan trước nếu có
        if has_images:
            cursor.execute("DELETE FROM image_resources WHERE type_detail_id IN (SELECT id FROM type_details);")
            print("Đã xóa dữ liệu liên quan từ bảng image_resources")
            
        if has_thumbnails:
            cursor.execute("DELETE FROM thumbnails WHERE type_detail_id IN (SELECT id FROM type_details);")
            print("Đã xóa dữ liệu liên quan từ bảng thumbnails")
            
        if has_cart_items:
            cursor.execute("DELETE FROM cart_items WHERE type_detail_id IN (SELECT id FROM type_details);")
            print("Đã xóa dữ liệu liên quan từ bảng cart_items")
        
        # Xóa dữ liệu từ bảng type_details
        cursor.execute("DELETE FROM type_details;")
        
        # Reset auto-increment counter cho bảng type_details
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='type_details';")
        
        # Hiển thị số bản ghi đã xóa
        print(f"Đã xóa {current_count} bản ghi từ bảng type_details")
        
        # Commit thay đổi
        conn.commit()
        
        # Bật lại foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Kiểm tra lại số lượng bản ghi sau khi xóa
        cursor.execute("SELECT COUNT(*) FROM type_details;")
        after_count = cursor.fetchone()[0]
        
        print(f"\nKiểm tra sau khi xóa: {after_count} bản ghi trong bảng type_details")
        print("Đã xóa thành công tất cả dữ liệu. Cấu trúc bảng type_details vẫn được giữ nguyên.")
        
        # Đóng kết nối
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False

def delete_table(db_path="app.db", table_name="type_details"):
    """Delete a table from the SQLite database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if not cursor.fetchone():
            print(f"Table '{table_name}' does not exist in the database")
            return False
        
        # Drop the table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table '{table_name}' successfully deleted")
        return True
    except Exception as e:
        print(f"Error deleting table: {e}")

def drop_rewards_table(db_path='app.db'):  # Thay đổi đường dẫn tới file database của bạn
    
    try:
        # Kết nối đến database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Xóa bảng rewards
        cursor.execute("DROP TABLE IF EXISTS rewards")
        
        # Commit thay đổi và đóng kết nối
        conn.commit()
        conn.close()
        
        print("Đã xóa thành công bảng rewards")
    except Exception as e:
        print(f"Lỗi khi xóa bảng rewards: {str(e)}")

if __name__ == "__main__":
    # Lấy đường dẫn đến database từ tham số dòng lệnh hoặc sử dụng giá trị mặc định
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Đường dẫn mặc định
        db_path = "sqlite_data/app.db"
        print(f"Sử dụng database mặc định: {db_path}")
        print("Gợi ý: Bạn có thể chỉ định đường dẫn database qua tham số dòng lệnh")
        print("Ví dụ: python show_tables.py path/to/your/database.sqlite")
    
    # Hiển thị danh sách bảng
    # show_all_tables(db_path)
    # drop_order_tables(db_path)
    # clear_all_tables(db_path)
    # clear_paint_types(db_path)
    # seed_paint_types1(db_path)
    # clear_type_details_with_sqlite(db_path)
    # delete_table(db_path)
    drop_rewards_table(db_path)
