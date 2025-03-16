# manual_delete.py
import os
import sys
import sqlite3


# Đường dẫn đến file database
DATABASE_PATH = r"E:\FABER APP\FABER_App_Backend\sqlite_data\app.db"

def delete_paint_type_by_name():
    # Kết nối với database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        paint_type_name = "Sơn chống thấm màu"
        print(f"Đang tìm và xóa loại sơn: {paint_type_name}")
        
        # Tìm paint_type để xem ID
        # cursor.execute("SELECT id, paint_type FROM paint_types WHERE paint_type = ?", (paint_type_name,))
        # paint_type = cursor.fetchone()
        cursor.execute("DELETE FROM paint_types WHERE id IS NULL")
        null_deleted = cursor.rowcount
        conn.commit()
        print(f"Đã xóa {null_deleted} bản ghi có id NULL")
            
    except Exception as e:
        conn.rollback()
        print(f"Lỗi khi xóa loại sơn: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_paint_type_by_name()