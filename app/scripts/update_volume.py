import sqlite3
from pathlib import Path

def update_volume_by_id(db_path, product_id, new_volume):
    """
    Cập nhật giá trị volume cho một sản phẩm cụ thể bằng ID
    
    Args:
        db_path: Đường dẫn đến file database SQLite
        product_id: ID của sản phẩm cần cập nhật
        new_volume: Giá trị volume mới
    """
    conn = None
    try:
        # Kết nối đến database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Đã kết nối đến database SQLite thành công.")
        
        # Kiểm tra xem sản phẩm có tồn tại không
        cursor.execute("SELECT id, product, code, volume FROM type_details WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            print(f"Không tìm thấy sản phẩm với ID: {product_id}")
            return False
        
        # Hiển thị thông tin sản phẩm trước khi cập nhật
        product_id, product_name, product_code, current_volume = product
        print(f"Thông tin sản phẩm trước khi cập nhật:")
        print(f"ID: {product_id}")
        print(f"Tên sản phẩm: {product_name}")
        print(f"Mã sản phẩm: {product_code}")
        print(f"Volume hiện tại: {current_volume}")
        
        # Cập nhật volume cho sản phẩm
        cursor.execute(
            "UPDATE type_details SET volume = ? WHERE id = ?",
            (new_volume, product_id)
        )
        
        # Lưu các thay đổi
        conn.commit()
        
        # Kiểm tra xem cập nhật có thành công không
        cursor.execute("SELECT volume FROM type_details WHERE id = ?", (product_id,))
        updated_volume = cursor.fetchone()[0]
        
        print(f"\nĐã cập nhật volume cho sản phẩm {product_name} (ID: {product_id}):")
        print(f"Volume cũ: {current_volume} → Volume mới: {updated_volume}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"Lỗi SQLite: {e}")
        return False
    except Exception as e:
        print(f"Lỗi: {e}")
        return False
    finally:
        # Đóng kết nối
        if conn:
            conn.close()
            print("\nĐã đóng kết nối database.")

if __name__ == "__main__":
    db_path = r"E:\FABER APP\FABER_App_Backend\sqlite_data\app.db"
    product_id = 4
    new_volume = 18.0
    update_volume_by_id(db_path, product_id, new_volume)