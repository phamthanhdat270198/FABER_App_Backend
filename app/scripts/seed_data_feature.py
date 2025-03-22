import os
import sys
import sqlite3
from app.db.base import engine, SessionLocal
from app.models.type_detail import TypeDetail

# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(root_dir)

# Đường dẫn đến file database
# DATABASE_PATH = os.path.join(root_dir, "sqlite_data", "app.db")

def seed_features_for_product(product_ids, feature_list):
    """
    Cập nhật tính năng cho các sản phẩm với ID và danh sách tính năng được chỉ định
    
    Args:
        product_ids: ID hoặc danh sách ID của các sản phẩm cần cập nhật
        feature_list: Danh sách các tính năng để gán cho sản phẩm
    """
    db = SessionLocal()
    try:
        # Đảm bảo product_ids là một list
        if not isinstance(product_ids, list):
            product_ids = [product_ids]
        
        # Kiểm tra xem có tính năng nào được cung cấp không
        if not feature_list or len(feature_list) == 0:
            print("Không có tính năng nào được cung cấp.")
            return
        
        # Lấy các sản phẩm theo ID
        products = db.query(TypeDetail).filter(TypeDetail.id.in_(product_ids)).all()
        
        if not products:
            print(f"Không tìm thấy sản phẩm nào với ID: {product_ids}")
            return
        
        # Cập nhật tính năng cho từng sản phẩm
        updated_count = 0
        
        for product in products:
            # Tạo chuỗi tính năng
            if len(feature_list) <= 2:
                # Sử dụng 'và' cho 2 tính năng
                features_text = "\n".join(feature_list)
            else:
                # Sử dụng dấu phẩy và 'và' cho nhiều tính năng
                features_text = ", ".join(feature_list[:-1]) + " và " + feature_list[-1]
            
            # Cập nhật trường features cho sản phẩm
            product.features = features_text
            updated_count += 1
            
            print(f"Đã cập nhật tính năng cho sản phẩm {product.product} (ID: {product.id})")
        
        # Commit thay đổi vào database
        db.commit()
        print(f"Đã cập nhật tính năng cho {updated_count}/{len(product_ids)} sản phẩm.")
        
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi seed dữ liệu tính năng: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

# Ví dụ sử dụng
if __name__ == "__main__":
    # Cập nhật tính năng cho sản phẩm có ID=1
    seed_features_for_product(5, ["Sơn bóng nội thất cao cấp", "Màng sơn bóng chắc, dẻo dai, màu sơn tươi sáng, độ phủ và chịu chùi rửa tối đa"])
    
    # Cập nhật tính năng cho nhiều sản phẩm cùng lúc
    # seed_features_for_product([2, 3, 4], ["Bền màu", "Không mùi"])