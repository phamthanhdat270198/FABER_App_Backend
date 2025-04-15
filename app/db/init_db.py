import os
import sys
import random
from datetime import datetime, timezone, timedelta, date
import traceback

import secrets
import base64
from PIL import Image
import io


# Thêm thư mục gốc vào sys.path để import module app
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir) 
root_dir = os.path.dirname(app_dir)
sys.path.append(root_dir)

from app.db.base import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
# from app.models.order import Order, OrderStatus
from app.models.paint_type import PaintType
from app.models.image_resource import ImageResource
from app.models.type_detail import TypeDetail
# from app.models.order_detail import OrderDetail
from app.models.token_store import TokenStore
from app.models.thumbnail import Thumbnail
from app.models.cart import Cart
from app.models.cart_items import CartItem
from app.models.rewards_info import RewardInfo, RewardType
import shutil
from pathlib import Path
from alembic import op
from app.core.security import get_password_hash

def get_date_time():
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)

    # Chuyển sang giờ Việt Nam (UTC+7)
    vn_time = utc_now.astimezone(timezone(timedelta(hours=7)))

    # Định dạng chuỗi
    # formatted_time = vn_time.strftime("%Y-%m-%d %H:%M:%S")
    return vn_time



def init_db():
    # Tạo tất cả các bảng trong database
    Base.metadata.create_all(bind=engine)
    print("Đã tạo các bảng thành công")

def seed_data():
    # Tạo session mới
    db = SessionLocal()
    try:
        # Kiểm tra xem đã có dữ liệu chưa
        user_count = db.query(User).count()
        if user_count == 0:
            # Thêm một số dữ liệu mẫu
            sample_users = [
                User(
                    ho_ten="Phạm Thành Đạt", 
                    dia_chi="Hà Nội", 
                    so_dien_thoai="0967496062", 
                    diem_thuong=1000000,
                    ngay_tao=get_date_time(),
                    hashed_password= get_password_hash("admin123"),
                    status = "ACCEPTED",
                    date_of_birth = date(1998, 1, 27),
                    gender = "Nam", 
                    admin = True
                ),
                User(
                    ho_ten="Lưu Trọng Hiếu", 
                    dia_chi="Nghệ An", 
                    so_dien_thoai="0372532690", 
                    diem_thuong=1000000,
                    ngay_tao=get_date_time(),
                    hashed_password= get_password_hash("admin123"),
                    status = "ACCEPTED",
                    gender = "Nam", 
                    admin = True
                )
            ]
            db.add_all(sample_users)
            db.commit()
            print("Đã thêm dữ liệu mẫu vào bảng users")
            
    except Exception as e:
        print(f"Lỗi khi thêm dữ liệu mẫu: {e}")
        traceback.print_exc()
    finally:
        db.close()

def seed_paint_type():
    db = SessionLocal()
    try:
        paint_types = db.query(PaintType).all()
        if not paint_types:
            print("Không có dữ liệu loại sơn trong database.")
            return
            
        # Cập nhật thông tin cho từng loại sơn
        for paint_type in paint_types:
            # Dựa vào tên loại sơn để thêm thông tin phù hợp
            if "Nước" in paint_type.paint_type:
                paint_type.mo_ta_san_pham = "Sơn nước cao cấp, thân thiện với môi trường, dễ lau chùi, có khả năng kháng khuẩn và chống bám bẩn."
                paint_type.thanh_phan = "Nhựa Acrylic, Titan Dioxide, bột màu, chất phụ gia đặc biệt và nước."
                paint_type.huong_dan_su_dung = "Khuấy đều sơn trước khi sử dụng. Sơn 2-3 lớp, mỗi lớp cách nhau 2-3 giờ. Dùng cọ, con lăn hoặc máy phun sơn."
                paint_type.luu_y = "Tránh sơn khi nhiệt độ dưới 10°C hoặc trên 35°C. Không sơn khi trời mưa hoặc độ ẩm cao."
                paint_type.bao_quan = "Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp và nhiệt độ cao. Đậy kín nắp sau khi sử dụng."
            
            elif "Dầu" in paint_type.paint_type:
                paint_type.mo_ta_san_pham = "Sơn dầu cao cấp, bền màu, chống thấm tốt, phù hợp cho bề mặt kim loại và gỗ, chịu được thời tiết khắc nghiệt."
                paint_type.thanh_phan = "Nhựa Alkyd, dầu, bột màu, chất phụ gia và dung môi."
                paint_type.huong_dan_su_dung = "Khuấy đều sơn trước khi sử dụng. Sơn 2-3 lớp, mỗi lớp cách nhau 6-8 giờ. Dùng cọ hoặc con lăn phù hợp."
                paint_type.luu_y = "Đảm bảo thông thoáng khi sử dụng. Tránh hút thuốc và các nguồn lửa khác. Sử dụng dụng cụ bảo hộ cá nhân."
                paint_type.bao_quan = "Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp. Đậy kín nắp sau khi sử dụng."
            
            elif "Chống Rỉ" in paint_type.paint_type:
                paint_type.mo_ta_san_pham = "Sơn lót đặc biệt ngăn chặn quá trình oxy hóa, bảo vệ bề mặt kim loại và chống ăn mòn hiệu quả."
                paint_type.thanh_phan = "Nhựa Epoxy, bột kẽm, chất chống ăn mòn, bột màu và dung môi."
                paint_type.huong_dan_su_dung = "Làm sạch bề mặt cần sơn. Khuấy đều sơn. Sơn 1-2 lớp, mỗi lớp cách nhau 4-6 giờ trước khi sơn phủ."
                paint_type.luu_y = "Phải làm sạch hoàn toàn vết rỉ trước khi sơn. Đảm bảo thông thoáng khi sử dụng."
                paint_type.bao_quan = "Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp. Đậy kín nắp sau khi sử dụng."
            
            elif "Epoxy" in paint_type.paint_type:
                paint_type.mo_ta_san_pham = "Sơn hai thành phần, độ bám dính và độ bền cao, chịu hóa chất, phù hợp cho sàn công nghiệp và bề mặt bê tông."
                paint_type.thanh_phan = "Nhựa Epoxy, chất đóng rắn, bột màu, phụ gia đặc biệt và dung môi."
                paint_type.huong_dan_su_dung = "Trộn hai thành phần theo tỷ lệ quy định. Sử dụng trong vòng 4-6 giờ sau khi trộn. Sơn 2 lớp, mỗi lớp cách nhau 8-12 giờ."
                paint_type.luu_y = "Không sử dụng khi nhiệt độ dưới 10°C. Đảm bảo thông thoáng khi sử dụng. Sơn sẽ cứng hoàn toàn sau 7 ngày."
                paint_type.bao_quan = "Bảo quản hai thành phần riêng biệt. Đậy kín nắp, để nơi khô ráo, thoáng mát."
            
            else:  # Mặc định cho các loại khác
                paint_type.mo_ta_san_pham = f"Sơn {paint_type.paint_type} chất lượng cao, đáp ứng các tiêu chuẩn về độ bền và an toàn."
                paint_type.thanh_phan = "Nhựa, bột màu, phụ gia và dung môi."
                paint_type.huong_dan_su_dung = "Khuấy đều sơn trước khi sử dụng. Sơn 2-3 lớp để có hiệu quả tốt nhất."
                paint_type.luu_y = "Đọc kỹ hướng dẫn trước khi sử dụng. Đảm bảo thông thoáng khi sơn."
                paint_type.bao_quan = "Bảo quản nơi khô ráo, thoáng mát, tránh ánh nắng trực tiếp. Đậy kín nắp sau khi sử dụng."
        
        db.commit()
        print(f"Đã cập nhật thông tin cho {len(paint_types)} loại sơn.")
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi cập nhật thông tin: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

    
def seed_image():
    """
    Seed images from faber_imgs folder into the database.
    
    Folder structure:
    faber_imgs/
        CODE1/
            5L.png
            18L.jpg
        CODE2/
            1L.jpg
            5L.png
            ...
    """
    db = SessionLocal()
    # Xác định đường dẫn tuyệt đối của thư mục gốc project
    current_file_path = os.path.abspath(__file__)
    project_path = os.path.dirname(os.path.dirname(current_file_path))
    image_paths = os.path.dirname(os.path.dirname(project_path))
    imgs_folder = "faber_imgs"
    img_path = os.path.join(image_paths, imgs_folder)
    # FE_path = "Faber-FE"
    # imgs_folder = r"faber_imgs"
    # img_path = os.path.join(image_paths, FE_path)
    # img_path = os.path.join(img_path, imgs_folder)
    
    try:
        # Get all type details
        type_details = db.query(TypeDetail).all()
        print(f"Found {len(type_details)} TypeDetail records")
        
        # Track statistics
        total_images_added = 0
        codes_not_found = []
        
        # Iterate through each code folder in the faber_imgs directory
        if not os.path.exists(img_path):
            print(f"Error: {img_path} directory not found!")
            return
            
        code_folders = os.listdir(img_path)
        print(f"Found {len(code_folders)} code folders in {img_path}")
        
        for code_folder in code_folders:
            folder_path = os.path.join(img_path, code_folder)
            if not os.path.isdir(folder_path):
                continue
                
            # Find all TypeDetails with this code
            matching_details = db.query(TypeDetail).filter(TypeDetail.code == code_folder).all()
            
            if not matching_details:
                codes_not_found.append(code_folder)
                print(f"Warning: No TypeDetail found with code {code_folder}")
                continue
                
            # Get all images in this folder
            image_files = [f for f in os.listdir(folder_path) 
                         if os.path.isfile(os.path.join(folder_path, f)) 
                         and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for image_file in image_files:
                # Try to extract volume from filename
                # Assuming filenames like "5L.png", "18L.jpg", etc.
                try:
                    volume_str = image_file.split('.')[0].replace('L', '')
                    volume = float(volume_str)
                except (ValueError, IndexError):
                    print(f"Warning: Could not extract volume from {image_file}, skipping")
                    continue
                
                # Find matching TypeDetail with both code and volume
                matching_detail = None
                for detail in matching_details:
                    if detail.volume == volume:
                        matching_detail = detail
                        break
                
                if not matching_detail:
                    print(f"Warning: No TypeDetail found with code={code_folder} and volume={volume}")
                    continue
                
                # Create relative image path
                image_path = os.path.join(code_folder, image_file)
                image_path = os.path.join(imgs_folder,image_path )
                # image_path = os.path.join(img_path,image_path )
                # img_vname = image_to_vname(image_path)
                # Check if image already exists for this TypeDetail
                existing_image = db.query(ImageResource).filter(
                    ImageResource.type_detail_id == matching_detail.id,
                    ImageResource.image_path == image_path
                ).first()
                
                if existing_image:
                    print(f"Image already exists for TypeDetail id={matching_detail.id}, path={image_path}")
                    continue
                
                # Create new ImageResource
                new_image = ImageResource(
                    image_path=image_path,
                    type_detail_id=matching_detail.id
                )
                
                db.add(new_image)
                total_images_added += 1
                print(f"Added image {image_path} to TypeDetail id={matching_detail.id} (code={code_folder}, volume={volume})")
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print(f"\nSummary:")
        print(f"Total images added: {total_images_added}")
        if codes_not_found:
            print(f"Codes not found in database: {', '.join(codes_not_found)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        raise
    finally:
        db.close()

def clear_existing_images():
    db = SessionLocal()
    """Clear all existing ImageResource records from the database."""
    try:
        # Count existing images
        image_count = db.query(ImageResource).count()
        print(f"Deleting {image_count} existing ImageResource records...")
        
        # Delete all image resources
        db.query(ImageResource).delete()
        db.commit()
        print(f"Successfully deleted all existing ImageResource records.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing existing images: {str(e)}")
        raise

def seed_type_detail():
    db = SessionLocal()
    try:
        # Thêm dữ liệu mẫu cho type_details
        type_detail_count = db.query(TypeDetail).count()
        if type_detail_count == 0:
            # Lấy các paint_types từ database
            paint_types = db.query(PaintType).all()
            
            if paint_types:
                # Tạo dữ liệu mẫu cho sơn nước (nếu có)
                son_min = next((pt for pt in paint_types if pt.paint_type == "Sơn mịn nội ngoại thất"), None)
                if son_min:
                    son_min_details = [
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="CLASSIC",
                            code="FB32",
                            package="Thùng",
                            volume=18.0,
                            price=920000,
                            m2_cover=80,
                            promotion="",
                            features= "Sơn mịn nội thất",
                            vname="Sơn mịn nội thất cao câp",
                            bonus_points = 2  
                        ),
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="SILVER",
                            code="FB505",
                            package="Thùng",
                            volume=18.0,
                            price=2360000,
                            m2_cover=90,
                            promotion="",
                            features= "Sơn mịn ngoại thất\nĐộ che phủ tốt, chống nấm mốc, chịu ẩm tốt",
                            vname="Sơn mịn ngoại thất cao cấp",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="SILVER",
                            code="FB505",
                            package="Lon",
                            volume=5.0,
                            price=750000,
                            m2_cover=27,
                            promotion="",
                            features= "Sơn mịn ngoại thất\nĐộ che phủ tốt, chống nấm mốc, chịu ẩm tốt",
                            vname="Sơn mịn ngoại thất cao cấp"
                        ),
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="SUPER WHITE",
                            code="FB33",
                            package="Thùng",
                            volume=18.0,
                            price=1880000,
                            m2_cover=90,
                            promotion="",
                            features= "Sơn siêu trắng trần nội thất cao cấp chuyên dụng\nMàng sơn trắng mịn, chống nấm mốc, chịu ẩm cao",
                            vname="Sơn siêu trắng trần",
                            bonus_points = 7
                        ),
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="SUPER WHITE",
                            code="FB33",
                            package="Lon",
                            volume=5.0,
                            price=590000,
                            m2_cover=22,
                            promotion="",
                            features= "Sơn siêu trắng trần nội thất cao cấp chuyên dụng\nMàng sơn trắng mịn, chống nấm mốc, chịu ẩm cao",
                            vname="Sơn siêu trắng trần",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="EASY CLEAN",
                            code="FB350",
                            package="Thùng",
                            volume=18.0,
                            price=2280000,
                            m2_cover=100,
                            promotion="",
                            features= "Sơn siêu mịn lau chùi nội thất cao cấp\nChống thấm tốt, chống nấm mốc, rửa sạch vết bẩn, độ bền màu cao",
                            vname="Sơn siêu mịn lau chùi",
                            bonus_points = 7
                        ),
                        TypeDetail(
                            paint_type_id=son_min.id,
                            product="EASY CLEAN",
                            code="FB350",
                            package="Lon",
                            volume=5.0,
                            price=670000,
                            m2_cover=25,
                            promotion="",
                            features= "Sơn siêu mịn lau chùi nội thất cao cấp\nChống thấm tốt, chống nấm mốc, rửa sạch vết bẩn, độ bền màu cao",
                            vname="Sơn siêu mịn lau chùi",
                            bonus_points = 2
                        )
                    ]
                    db.add_all(son_min_details)
                
                # Tạo dữ liệu mẫu cho sơn dầu (nếu có)
                son_bong = next((pt for pt in paint_types if pt.paint_type == "Sơn bóng nội ngoại thất"), None)
                if son_bong:
                    son_bong_details = [
                        TypeDetail(
                            paint_type_id=son_bong.id,
                            product="SATIN",
                            code="FB365",
                            package="Thùng",
                            volume=18.0,
                            price=3270000,
                            m2_cover=115,
                            promotion="",
                            features= "Sơn bóng nội thất cao cấp\nMàng sơn bóng chắc, dẻo dai, màu sơn tươi sáng, độ phủ và chịu chùi rửa tối đa",
                            vname="Sơn bóng nội",
                            bonus_points = 7
                        ),
                        TypeDetail(
                            paint_type_id=son_bong.id,
                            product="SATIN",
                            code="FB365",
                            package="Lon",
                            volume=5.0,
                            price=1070000,
                            m2_cover=32,
                            promotion="",
                            features= "Sơn bóng nội thất cao cấp\nMàng sơn bóng chắc, dẻo dai, màu sơn tươi sáng, độ phủ và chịu chùi rửa tối đa",
                            vname="Sơn bóng nội",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_bong.id,
                            product="NANO SHIELD",
                            code="FB536",
                            package="Lon",
                            volume=5.0,
                            price=750000,
                            m2_cover=35,
                            promotion="",
                            features= "Sơn bóng ngoại thất cao cấp\nMàng sơn bóng chắc, dẻo dai, màu sơn tươi sáng, độ phủ và chịu chùi rửa tối đa",
                            vname="Sơn bóng ngoại",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_bong.id,
                            product="NANO SHIELD",
                            code="FB536",
                            package="Thùng",
                            volume=18.0,
                            price=4080000,
                            m2_cover=130,
                            promotion="",
                            features= "Sơn bóng ngoại thất cao cấp\nMàng sơn bóng chắc, dẻo dai, màu sơn tươi sáng, độ phủ và chịu chùi rửa tối đa",
                            vname="Sơn bóng ngoại",
                            bonus_points = 7
                        )
                    ]
                    db.add_all(son_bong_details)
                
                # Tạo dữ liệu mẫu cho sơn epoxy (nếu có)
                son_chong_tham_mau = next((pt for pt in paint_types if pt.paint_type == "Sơn chống thấm"), None)
                if son_chong_tham_mau:
                    son_chong_tham_mau_details = [
                        TypeDetail(
                            paint_type_id=son_chong_tham_mau.id,
                            product="COLOR POWER",
                            code="FB845",
                            package="Thùng",
                            volume=18.0,
                            price=3760000,
                            m2_cover=85,
                            promotion="",
                            features= "Sơn chống thấm màu Acrylic\nChống thấm vượt trội, che phủ tuyệt đối, chống nóng, độ bền cao",
                            vname="Sơn chống thấm màu",
                            bonus_points = 7
                        ),
                        TypeDetail(
                            paint_type_id=son_chong_tham_mau.id,
                            product="COLOR POWER",
                            code="FB845",
                            package="Lon",
                            volume=5.0,
                            price=3760000,
                            m2_cover=15,
                            promotion="",
                            features= "Sơn chống thấm màu Acrylic\nChống thấm vượt trội, che phủ tuyệt đối, chống nóng, độ bền cao",
                            vname="Sơn chống thấm màu",
                            bonus_points = 2
                        )
                    ]
                    db.add_all(son_chong_tham_mau_details)

                # Tạo dữ liệu mẫu cho  Sơn lót chống kiềm (nếu có)
                son_lot_chong_kiem = next((pt for pt in paint_types if pt.paint_type == "Sơn lót chống kiềm"), None)
                if son_lot_chong_kiem:
                    son_lot_chong_kiem_details = [
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="PRIMER ULTRA",
                            code="M35",
                            package="Thùng",
                            volume=18.0,
                            price=4550000,
                            m2_cover=120,
                            promotion="",
                            features= "Sơn lót siêu kháng kiềm muối tường ẩm\nChống kiềm muối đặc biệt",
                            vname="Sơn lót siêu kháng kiềm muối ngoại thất đặc biệt",
                            bonus_points = 10
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="PRIMER ULTRA",
                            code="M35",
                            package="Lon",
                            volume=5.0,
                            price=1350000,
                            m2_cover=35,
                            promotion="",
                            features= "Sơn lót siêu kháng kiềm muối tường ẩm\nChống kiềm muối đặc biệt",
                            vname="Sơn lót siêu kháng kiềm muối ngoại thất đặc biệt",
                            bonus_points = 3
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="SEALER MAX",
                            code="M11",
                            package="Thùng",
                            volume=18.0,
                            price=2370000,
                            m2_cover=120,
                            promotion="",
                            features= "Sơn lót kháng kiềm nội thất đặc biệt\nKháng kiềm, chống rêu mốc, tăng độ bám dính, chống loang ố",
                            vname="Sơn lót kháng kiềm muối nội thất đặc biệt",
                            bonus_points = 10
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="SEALER MAX",
                            code="M11",
                            package="Lon",
                            volume=5.0,
                            price=770000,
                            m2_cover=35,
                            promotion="",
                            features= "Sơn lót kháng kiềm nội thất đặc biệt\nKháng kiềm, chống rêu mốc, tăng độ bám dính, chống loang ố",
                            vname="Sơn lót kháng kiềm muối nội thất đặc biệt",
                            bonus_points = 3
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="PRIMER",
                            code="FB23",
                            package="Thùng",
                            volume=18.0,
                            price=2660000,
                            m2_cover=120,
                            promotion="",
                            features= "Sơn lót kháng kiềm ngoại thất\nKháng kiềm, nấm mốc, tăng độ bám dính",
                            vname="Sơn lót ngoại thất eco",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="PLATINUM PRIMER",
                            code="FB25",
                            package="Thùng",
                            volume=18.0,
                            price=3410000,
                            m2_cover=120,
                            promotion="",
                            features= "Sơn lót kháng kiềm ngoại thất cao cấp\nChống muối, chống nấm mốc, chống phấn hóa, độ bền cao",
                            vname="Sơn lót kháng kiềm ngoại thất cao cấp",
                            bonus_points = 7
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="PLATINUM PRIMER",
                            code="FB25",
                            package="Lon",
                            volume=5.0,
                            price=1060000,
                            m2_cover=35,
                            promotion="",
                            features= "Sơn lót kháng kiềm ngoại thất cao cấp\nChống muối, chống nấm mốc, chống phấn hóa, độ bền cao",
                            vname="Sơn lót kháng kiềm ngoại thất cao cấp",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="SEALER",
                            code="FB01",
                            package="Thùng",
                            volume=18.0,
                            price=1790000,
                            m2_cover=110,
                            promotion="",
                            features= "Sơn lót kháng kiềm nội thất\nKháng kiềm, chống nấm mốc, tăng độ bám dính, độ phủ",
                            vname="Sơn lót nội thất eco",
                            bonus_points = 2
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="SEALER PLUS",
                            code="FB102",
                            package="Thùng",
                            volume=18.0,
                            price=2250000,
                            m2_cover=115,
                            promotion="",
                            features= "Sơn lót kháng kiềm nội thất cao cấp\nThẩm thấu, bám dính, độ phủ cao, chống phấn hóa, chống loang ố màu",
                            vname="Sơn lót nội thất cao cấp",
                            bonus_points = 7
                        ),
                        TypeDetail(
                            paint_type_id=son_lot_chong_kiem.id,
                            product="SEALER PLUS",
                            code="FB102",
                            package="Thùng",
                            volume=5.0,
                            price=690000,
                            m2_cover=33,
                            promotion="",
                            features= "Sơn lót kháng kiềm nội thất cao cấp\nThẩm thấu, bám dính, độ phủ cao, chống phấn hóa, chống loang ố màu",
                            vname="Sơn lót nội thất cao cấp",
                            bonus_points = 2
                        )
                    ]
                    db.add_all(son_lot_chong_kiem_details)

                # Tạo dữ liệu mẫu cho Sơn siêu bóng men sứ (nếu có)
                metro_lux = next((pt for pt in paint_types if pt.paint_type == "Sơn siêu bóng men sứ"), None)
                if metro_lux:
                    metro_lux_details = [
                        TypeDetail(
                            paint_type_id=metro_lux.id,
                            product="CRYSTAL",
                            code="M12",
                            package="Thùng",
                            volume=15.0,
                            price=4200000,
                            m2_cover=120,
                            promotion="",
                            features= "Sơn siêu bóng men sứ nội thất cao cấp\nMàng sơn siêu bóng, sang trọng, đanh chắc, chống nấm mốc, chùi rửa tối đa",
                            vname="Sơn bóng men sứ nội thất",
                            bonus_points = 15
                        ),
                        TypeDetail(
                            paint_type_id=metro_lux.id,
                            product="CRYSTAL",
                            code="M12",
                            package="Lon",
                            volume=5.0,
                            price=1380000,
                            m2_cover=30,
                            promotion="",
                            features= "Sơn siêu bóng men sứ nội thất cao cấp\nMàng sơn siêu bóng, sang trọng, đanh chắc, chống nấm mốc, chùi rửa tối đa",
                            vname="Sơn bóng men sứ nội thất",
                            bonus_points = 3
                        ),
                        TypeDetail(
                            paint_type_id=metro_lux.id,
                            product="CRYSTAL",
                            code="M12",
                            package="Lon",
                            volume=1.0,
                            price=375000,
                            m2_cover=10,
                            promotion="",
                            features= "Sơn siêu bóng men sứ nội thất cao cấp\nMàng sơn siêu bóng, sang trọng, đanh chắc, chống nấm mốc, chùi rửa tối đa",
                            vname="Sơn bóng men sứ nội thất"  # Để trống hoặc thêm dữ liệu vname thực tế
                        ),
                        TypeDetail(
                            paint_type_id=metro_lux.id,
                            product="ANAMEL",
                            code="M38",
                            package="Thùng",
                            volume=15.0,
                            price=5850000,
                            m2_cover=120,
                            promotion="",
                            features= "Sơn men sứ chống bám bụi cao cấp\nChống bám bụi, chống nóng, chống phai màu, bề mặt đánh cứng",
                            vname="Sơn bóng men sứ ngoại thất chống bám bụi",
                            bonus_points = 15
                        ),
                        TypeDetail(
                            paint_type_id=metro_lux.id,
                            product="ANAMEL",
                            code="M38",
                            package="Lon",
                            volume=5.0,
                            price=2350000,
                            m2_cover=30,
                            promotion="",
                            features= "Sơn men sứ chống bám bụi cao cấp\nChống bám bụi, chống nóng, chống phai màu, bề mặt đánh cứng",
                            vname="Sơn bóng men sứ ngoại thất chống bám bụi",
                            bonus_points = 3
                        ),
                        TypeDetail(
                            paint_type_id=metro_lux.id,
                            product="ANAMEL",
                            code="M38",
                            package="Lon",
                            volume=1.0,
                            price=550000,
                            m2_cover=10,
                            promotion="",
                            features= "Sơn men sứ chống bám bụi cao cấp\nChống bám bụi, chống nóng, chống phai màu, bề mặt đánh cứng",
                            vname="Sơn bóng men sứ ngoại thất chống bám bụi"  # Để trống hoặc thêm dữ liệu vname thực tế
                        )
                    ]
                    db.add_all(metro_lux_details)
            
            db.commit()
            print("Đã thêm dữ liệu mẫu vào bảng type_details")
    finally:
        db.close()

def seed_token_store():
    db = SessionLocal()
    try:
        # Kiểm tra xem đã có dữ liệu trong bảng token_store chưa
        token_count = db.query(TokenStore).count()
        if token_count > 0:
            print(f"Bảng token_store đã có {token_count} bản ghi.")
            overwrite = input("Bạn có muốn xóa dữ liệu hiện tại và tạo dữ liệu mẫu mới không? (y/n): ")
            if overwrite.lower() != 'y':
                print("Hủy bỏ việc tạo dữ liệu mẫu.")
                return
            
            # Xóa dữ liệu hiện tại
            db.query(TokenStore).delete()
            db.commit()
            print("Đã xóa dữ liệu cũ trong bảng token_store.")
        
        # Lấy danh sách người dùng hiện có
        users = db.query(User).all()
        
        if not users:
            print("Không có người dùng trong database. Hãy tạo người dùng trước.")
            return
        
        # Các user agent phổ biến để tạo dữ liệu giả
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        ]
        
        # Tạo dữ liệu mẫu cho mỗi người dùng
        tokens_created = 0
        now = datetime.utcnow()
        
        for user in users:
            # Số lượng token ngẫu nhiên cho mỗi người dùng (1-3)
            num_tokens = random.randint(1, 3)
            
            for i in range(num_tokens):
                # Tạo token với các trạng thái khác nhau
                token_type = random.choice(["valid", "expired", "revoked"])
                token = secrets.token_hex(32)  # 64 ký tự hex
                device_info = random.choice(user_agents)
                
                # Thiết lập thời gian tạo và thời gian hết hạn
                created_delta = timedelta(days=random.randint(1, 60))  # 1-60 ngày trước
                created_at = now - created_delta
                
                if token_type == "valid":
                    # Token còn hạn (30 ngày từ ngày tạo)
                    expires_at = created_at + timedelta(days=30)
                    is_revoked = False
                elif token_type == "expired":
                    # Token đã hết hạn
                    expires_at = created_at + timedelta(days=random.randint(1, 10))
                    is_revoked = False
                else:  # "revoked"
                    # Token đã bị thu hồi (có thể còn hạn hoặc hết hạn)
                    expires_at = created_at + timedelta(days=30)
                    is_revoked = True
                
                # Thời gian sử dụng lần cuối (ngẫu nhiên giữa thời gian tạo và hiện tại)
                if now < expires_at and not is_revoked:
                    # Nếu token còn hiệu lực, last_used có thể là gần đây
                    last_used_delta = timedelta(days=random.randint(0, min(30, int(created_delta.days))))
                    last_used_at = now - last_used_delta
                else:
                    # Nếu token đã hết hạn hoặc thu hồi, last_used_at phải trước thời điểm đó
                    max_days = min(created_delta.days, (expires_at - created_at).days)
                    last_used_delta = timedelta(days=random.randint(0, max_days))
                    last_used_at = created_at + last_used_delta
                
                # Tạo bản ghi token
                token_store = TokenStore(
                    user_id=user.id,
                    token=token,
                    expires_at=expires_at,
                    is_revoked=is_revoked,
                    device_info=device_info,
                    created_at=created_at,
                    last_used_at=last_used_at
                )
                
                db.add(token_store)
                tokens_created += 1
        
        db.commit()
        print(f"Đã tạo thành công {tokens_created} token mẫu cho {len(users)} người dùng!")
        
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi tạo dữ liệu mẫu: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def clear_existing_thumbnails():
    db = SessionLocal()
    """Clear all existing Thumbnail records from the database."""
    try:
        # Count existing thumbnails
        thumbnail_count = db.query(Thumbnail).count()
        print(f"Deleting {thumbnail_count} existing Thumbnail records...")
        
        # Delete all thumbnails
        db.query(Thumbnail).delete()
        db.commit()
        print(f"Successfully deleted all existing Thumbnail records.")
    except Exception as e:
        db.rollback()
        print(f"Error clearing existing thumbnails: {str(e)}")
        raise

def seed_thumbnails():
    """
    Seed thumbnails from faber_thumbs folder into the database.
    First clears all existing Thumbnail records, then adds new ones.
    
    Folder structure:
    faber_thumbs/
        CODE1/
            5L.png
            18L.jpg
        CODE2/
            1L.jpg
            5L.png
            ...
    """
    db = SessionLocal()
    # Xác định đường dẫn tuyệt đối của thư mục gốc project
    current_file_path = os.path.abspath(__file__)
    project_path = os.path.dirname(os.path.dirname(current_file_path))
    image_paths = os.path.dirname(os.path.dirname(project_path))
    imgs_folder = "faber_thumbs"
    thumb_path = os.path.join(image_paths, imgs_folder)
    # FE_path = "Faber-FE"
    # thumbs_folder = r"assets\faber_thumbs"
    # thumb_path = os.path.join(image_paths, FE_path)
    # thumb_path = os.path.join(thumb_path, thumbs_folder)
    # print("thumbnail path = ", thumb_path)
    try:
        
        # Get all type details
        type_details = db.query(TypeDetail).all()
        print(f"Found {len(type_details)} TypeDetail records")
        
        # Track statistics
        total_thumbnails_added = 0
        codes_not_found = []
        
        # Iterate through each code folder in the thumbnail directory
        if not os.path.exists(thumb_path):
            print(f"Error: {thumb_path} directory not found!")
            return
            
        code_folders = os.listdir(thumb_path)
        print(f"Found {len(code_folders)} code folders in {thumb_path}")
        
        for code_folder in code_folders:
            folder_path = os.path.join(thumb_path , code_folder)
            if not os.path.isdir(folder_path):
                continue
                
            # Find all TypeDetails with this code
            matching_details = db.query(TypeDetail).filter(TypeDetail.code == code_folder).all()
            
            if not matching_details:
                codes_not_found.append(code_folder)
                print(f"Warning: No TypeDetail found with code {code_folder}")
                continue
                
            # Get all thumbnail images in this folder
            thumbnail_files = [f for f in os.listdir(folder_path) 
                             if os.path.isfile(os.path.join(folder_path, f)) 
                             and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for thumbnail_file in thumbnail_files:
                # Try to extract volume from filename
                # Assuming filenames like "5L.png", "18L.jpg", etc.
                try:
                    volume_str = thumbnail_file.split('.')[0].replace('L', '')
                    volume = float(volume_str)
                except (ValueError, IndexError):
                    print(f"Warning: Could not extract volume from {thumbnail_file}, skipping")
                    continue
                
                # Find matching TypeDetail with both code and volume
                matching_detail = None
                for detail in matching_details:
                    if detail.volume == volume:
                        matching_detail = detail
                        break
                
                if not matching_detail:
                    print(f"Warning: No TypeDetail found with code={code_folder} and volume={volume}")
                    continue
                
                # Create relative thumbnail path
                thumbnail_path = os.path.join(code_folder, thumbnail_file)
                thumbnail_path = os.path.join(imgs_folder, thumbnail_path)
                # thumbnail_path = os.path.join(thumb_path, thumbnail_path)
                # img_vname = image_to_vname(thumbnail_path)
                # print("type image base ==== ", type(img_vname))
                # Check if thumbnail already exists for this TypeDetail
                existing_thumbnail = db.query(Thumbnail).filter(
                    Thumbnail.type_detail_id == matching_detail.id,
                    Thumbnail.path_to_thumbnail == thumbnail_path
                ).first()
                
                if existing_thumbnail:
                    print(f"Thumbnail already exists for TypeDetail id={matching_detail.id}, path={thumbnail_path}")
                    continue
                
                # Create new Thumbnail
                new_thumbnail = Thumbnail(
                    path_to_thumbnail=thumbnail_path,
                    type_detail_id=matching_detail.id
                )
                
                db.add(new_thumbnail)
                total_thumbnails_added += 1
                print(f"Added thumbnail {thumbnail_path} to TypeDetail id={matching_detail.id} (code={code_folder}, volume={volume})")
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print(f"\nSummary:")
        print(f"Total thumbnails added: {total_thumbnails_added}")
        if codes_not_found:
            print(f"Codes not found in database: {', '.join(codes_not_found)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")
        raise
    finally:
        db.close()

def seed_rewards():
    db = SessionLocal()
    # Xóa dữ liệu cũ (tùy chọn)
    current_file_path = os.path.abspath(__file__)
    project_path = os.path.dirname(os.path.dirname(current_file_path))
    image_paths = os.path.dirname(os.path.dirname(project_path))
    imgs_folder = "faber_reward_imgs"
    db.query(RewardInfo).delete()
    
    # Phần thưởng thông thường
    regular_rewards = [
        RewardInfo(
            name="Nồi chiên không dầu",
            type=RewardType.REGULAR,
            is_special=False,
            image_url="faber_reward_imgs/noi_chien.png"
        ),
        RewardInfo(
            name="Máy lọc không khí",
            type=RewardType.REGULAR,
            is_special=False,
            image_url="faber_reward_imgs/may_loc_kk.png"
        ),
        RewardInfo(
            name="Máy hút bụi cầm tay",
            type=RewardType.REGULAR,
            is_special=False,
            image_url="faber_reward_imgs/may_hut_bui.png"
        ),

        RewardInfo(
            name="2 thùng sơn lót nội thất cao cấp",
            type=RewardType.REGULAR,
            is_special=False,
            image_url="faber_reward_imgs/son.jpg"
        )
    ]
    #phần thưởng seeding
    ignore_rewards = [
        RewardInfo(
            name="TV Samsung",
            type=RewardType.IGNORE,
            is_special=False,
            image_url="faber_reward_imgs/tv_samsung.jpg"
        )
    ]
    # Phần thưởng đặc biệt
    special_rewards = [
        RewardInfo(
            name="Nửa chỉ vàng",
            type=RewardType.SPECIAL,
            is_special=True,
            special_spin_number=5,
            image_url="faber_reward_imgs/vang.jpg"
        ),
        RewardInfo(
            name="1 chỉ vàng",
            type=RewardType.SPECIAL,
            is_special=True,
            special_spin_number=9,
            image_url="faber_reward_imgs/vang.png"
        ),
        RewardInfo(
            name="Xe Vision",
            type=RewardType.SPECIAL,
            is_special=True,
            special_spin_number=15,
            image_url="faber_reward_imgs/xe_vision.png"
        )
    ]
    
    # Thêm tất cả phần thưởng vào database
    db.add_all(regular_rewards + ignore_rewards + special_rewards )
    db.commit()
    
    print(f"Đã seed {len(regular_rewards)} phần thưởng thông thường và {len(special_rewards)} phần thưởng đặc biệt")

if __name__ == "__main__":
    try:
        print("Bắt đầu khởi tạo database...")
        init_db()
        # seed_data()
        # seed_paint_type()
        # clear_existing_images()
        # seed_image()
        # clear_existing_thumbnails()
        # seed_thumbnails()
        # seed_product_images()
        # seed_type_detail()
        # seed_order_detail()
        # seed_token_store()
        # seed_rewards()
        print("Khởi tạo database hoàn tất!")
    except Exception as e:
        print(f"Lỗi: {e}")
        traceback.print_exc()