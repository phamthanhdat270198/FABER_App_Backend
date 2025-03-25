import os
import sys
import uuid
import random
from datetime import datetime, timedelta
import traceback
import secrets

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
import shutil
from pathlib import Path
from alembic import op


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
                    ho_ten="Nguyễn Văn A", 
                    dia_chi="123 Đường Lê Lợi, Quận 1, TP.HCM", 
                    so_dien_thoai="0901234567", 
                    diem_thuong=100.0
                ),
                User(
                    ho_ten="Trần Thị B", 
                    dia_chi="456 Đường Nguyễn Huệ, Quận 1, TP.HCM", 
                    so_dien_thoai="0912345678", 
                    diem_thuong=150.5
                ),
            ]
            db.add_all(sample_users)
            db.commit()
            print("Đã thêm dữ liệu mẫu vào bảng users")
            
        # Kiểm tra xem bảng orders đã có dữ liệu chưa
        order_count = db.query(Order).count()
        if order_count == 0:
            # Lấy users từ database để tạo orders
            users = db.query(User).all()
            if users:
                sample_orders = [
                    Order(
                        user_id=users[0].id,
                        date_time=datetime.utcnow() - timedelta(days=2),
                        status=OrderStatus.ACCEPT,
                        is_deleted=False
                    ),
                    Order(
                        user_id=users[0].id,
                        date_time=datetime.utcnow() - timedelta(days=1),
                        status=OrderStatus.PENDING,
                        is_deleted=False
                    ),
                ]
                
                if len(users) > 1:
                    sample_orders.append(
                        Order(
                            user_id=users[1].id,
                            date_time=datetime.utcnow() - timedelta(hours=12),
                            status=OrderStatus.PENDING,
                            is_deleted=False
                        )
                    )
                
                db.add_all(sample_orders)
                db.commit()
                print("Đã thêm dữ liệu mẫu vào bảng orders")
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
    db = SessionLocal()
    img_path = r"E:\FABER APP\faber_imgs"
    try:
        # Thêm dữ liệu mẫu cho image_resources
        image_count = db.query(ImageResource).count()
        if image_count == 0:
            sample_images = []
            for img_name in os.listdir(img_path):
                image_path = os.path.join(img_path, img_name)
                img_resource = ImageResource(
                    image_path=image_path
                )
                sample_images.append(img_resource)
            
            db.add_all(sample_images)
            db.commit()
            print("Đã thêm dữ liệu mẫu vào bảng image_resources")
    finally:
        db.close()

def seed_product_images():
    db = SessionLocal()
    try:
        # Lấy tất cả sản phẩm từ database
        products = db.query(TypeDetail).all()
        
        if not products:
            print("Không có sản phẩm trong database.")
            return
        
        # Danh sách đường dẫn ảnh mẫu cho các loại sản phẩm
        sample_image_paths = {
            "Sơn Nước": [
                "/uploads/images/products/son_nuoc_1.jpg",
                "/uploads/images/products/son_nuoc_2.jpg",
                "/uploads/images/products/son_nuoc_3.jpg",
                "/uploads/images/products/son_nuoc_4.jpg"
            ],
            "Sơn Dầu": [
                "/uploads/images/products/son_dau_1.jpg",
                "/uploads/images/products/son_dau_2.jpg",
                "/uploads/images/products/son_dau_3.jpg"
            ],
            "Sơn Epoxy": [
                "/uploads/images/products/son_epoxy_1.jpg",
                "/uploads/images/products/son_epoxy_2.jpg",
                "/uploads/images/products/son_epoxy_3.jpg",
                "/uploads/images/products/son_epoxy_4.jpg",
                "/uploads/images/products/son_epoxy_5.jpg"
            ],
            "Sơn Chống Rỉ": [
                "/uploads/images/products/son_chong_ri_1.jpg",
                "/uploads/images/products/son_chong_ri_2.jpg",
                "/uploads/images/products/son_chong_ri_3.jpg"
            ],
            "default": [
                "/uploads/images/products/paint_1.jpg",
                "/uploads/images/products/paint_2.jpg",
                "/uploads/images/products/paint_3.jpg"
            ]
        }
        
        # Xóa ảnh cũ (tùy chọn)
        delete_existing = input("Bạn có muốn xóa tất cả ảnh cũ không? (y/n): ")
        if delete_existing.lower() == 'y':
            db.query(ImageResource).delete()
            print("Đã xóa tất cả ảnh cũ.")
        
        # Thêm ảnh cho mỗi sản phẩm
        images_added = 0
        
        for product in products:
            # Xác định loại sơn của sản phẩm
            paint_type_name = db.query(PaintType.paint_type).join(TypeDetail).filter(TypeDetail.id == product.id).scalar()
            # paint_type_name = product.paint_type
            # Chọn đường dẫn ảnh phù hợp với loại sơn
            image_paths = []
            for key in sample_image_paths:
                if key in paint_type_name:
                    image_paths = sample_image_paths[key]
                    break
            
            # Nếu không tìm thấy loại phù hợp, dùng mặc định
            if not image_paths:
                image_paths = sample_image_paths["default"]
            
            # Số lượng ảnh ngẫu nhiên cho mỗi sản phẩm (2-4)
            num_images = random.randint(2, min(4, len(image_paths)))
            selected_paths = random.sample(image_paths, num_images)
            
            # Thêm ảnh cho sản phẩm
            for path in selected_paths:
                # Thêm mã sản phẩm vào đường dẫn để làm cho nó độc đáo hơn
                unique_path = path.replace(".jpg", f"_{product.code}_{random.randint(100, 999)}.jpg")
                
                image = ImageResource(
                    image_path=unique_path,
                    type_detail_id=product.id
                )
                db.add(image)
                images_added += 1
        
        db.commit()
        print(f"Đã thêm {images_added} ảnh cho {len(products)} sản phẩm.")
        
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi thêm ảnh sản phẩm: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


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
                son_nuoc = next((pt for pt in paint_types if pt.paint_type == "Sơn Nước"), None)
                if son_nuoc:
                    son_nuoc_details = [
                        TypeDetail(
                            paint_type_id=son_nuoc.id,
                            product="Dulux Easyclean Plus",
                            code="DLX-ECP-01",
                            package="Thùng",
                            volume=5.0,
                            price=1250000,
                            m2_cover=60.0,
                            promotion="Giảm 10% đến cuối tháng",
                            base64=None  # Để trống hoặc thêm dữ liệu base64 thực tế
                        ),
                        TypeDetail(
                            paint_type_id=son_nuoc.id,
                            product="Jotun Majestic True Beauty Sheen",
                            code="JOTUN-MTB-02",
                            package="Thùng",
                            volume=5.0,
                            price=1420000,
                            m2_cover=65.0,
                            promotion=None,
                            base64=None
                        ),
                    ]
                    db.add_all(son_nuoc_details)
                
                # Tạo dữ liệu mẫu cho sơn dầu (nếu có)
                son_dau = next((pt for pt in paint_types if pt.paint_type == "Sơn Dầu"), None)
                if son_dau:
                    son_dau_details = [
                        TypeDetail(
                            paint_type_id=son_dau.id,
                            product="Nippon Oil-based Enamel",
                            code="NIP-OBE-01",
                            package="Lon",
                            volume=1.0,
                            price=180000,
                            m2_cover=12.0,
                            promotion=None,
                            base64=None
                        ),
                    ]
                    db.add_all(son_dau_details)
                
                # Tạo dữ liệu mẫu cho sơn epoxy (nếu có)
                son_epoxy = next((pt for pt in paint_types if pt.paint_type == "Sơn Epoxy"), None)
                if son_epoxy:
                    son_epoxy_details = [
                        TypeDetail(
                            paint_type_id=son_epoxy.id,
                            product="Jotun Jotafloor PU Topcoat",
                            code="JOT-JFPU-01",
                            package="Bộ",
                            volume=5.0,
                            price=2500000,
                            m2_cover=50.0,
                            promotion="Tặng kèm bộ dụng cụ thi công",
                            base64=None
                        ),
                        TypeDetail(
                            paint_type_id=son_epoxy.id,
                            product="Cadin Epoxy Floor CD-500",
                            code="CAD-EP-500",
                            package="Bộ",
                            volume=5.0,
                            price=1800000,
                            m2_cover=45.0,
                            promotion=None,
                            base64=None
                        ),
                    ]
                    db.add_all(son_epoxy_details)
            
            db.commit()
            print("Đã thêm dữ liệu mẫu vào bảng type_details")
    finally:
        db.close()

def seed_order_detail():
    db = SessionLocal()
    try:
        # Code đã có cho User, Order, PaintType, ImageResource, TypeDetail
        # ...
        
        # Thêm dữ liệu mẫu cho order_details
        order_detail_count = db.query(OrderDetail).count()
        if order_detail_count == 0:
            # Lấy orders và type_details từ database
            orders = db.query(Order).all()
            type_details = db.query(TypeDetail).all()
            
            if orders and type_details:
                sample_order_details = []
                
                # Tạo dữ liệu cho mỗi order
                for order in orders:
                    # Chọn ngẫu nhiên từ 1-3 sản phẩm cho mỗi đơn hàng
                    num_products = random.randint(1, min(3, len(type_details)))
                    selected_type_details = random.sample(type_details, num_products)
                    
                    for td in selected_type_details:
                        # Nếu có giá sản phẩm, sử dụng nó để tính total_amount
                        if td.price:
                            quantity = random.randint(1, 5)
                            total_amount = quantity * td.price
                            
                            sample_order_details.append(
                                OrderDetail(
                                    order_id=order.id,
                                    type_detail_id=td.id,
                                    quantity=quantity,
                                    total_amount=total_amount
                                )
                            )
                
                if sample_order_details:
                    db.add_all(sample_order_details)
                    db.commit()
                    print(f"Đã thêm {len(sample_order_details)} dữ liệu mẫu vào bảng order_details")
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

def seed_thumbnail_data():
    db = SessionLocal()
    try:
        # Lấy tất cả sản phẩm từ database
        products = db.query(TypeDetail).all()
        
        if not products:
            print("Không có sản phẩm trong database.")
            return
        
        # Tạo thư mục lưu trữ thumbnail nếu chưa tồn tại
        thumbnails_dir = Path(root_dir) / "static" / "thumbnails"
        thumbnails_dir.mkdir(parents=True, exist_ok=True)
        
        # Các mẫu tên file ảnh giả lập
        sample_image_names = [
            "product_thumbnail_1.jpg",
            "product_thumbnail_2.png",
            "product_image_small.jpg",
            "product_preview.png",
            "thumbnail_preview.jpg",
            "small_preview.png",
            "color_sample.jpg",
            "product_detail.png",
            "paint_sample.jpg",
            "color_palette.png"
        ]
        
        # Thêm thumbnail cho mỗi sản phẩm
        thumbnails_added = 0
        
        for product in products:
            # Kiểm tra xem sản phẩm đã có thumbnail chưa
            existing_thumbnail = db.query(Thumbnail).filter(Thumbnail.type_detail_id == product.id).first()
            
            if not existing_thumbnail:
                # Chọn ngẫu nhiên một tên file
                image_name = random.choice(sample_image_names)
                
                # Tạo đường dẫn giả lập
                path_to_thumbnail = f"/static/thumbnails/{product.code}_{image_name}" if product.code else f"/static/thumbnails/product_{product.id}_{image_name}"
                
                # Tạo bản ghi trong database mà không cần tạo file thực
                thumbnail = Thumbnail(
                    type_detail_id=product.id,
                    path_to_thumbnail=path_to_thumbnail
                )
                db.add(thumbnail)
                thumbnails_added += 1
                
                # Thêm nhiều hơn một thumbnail cho một số sản phẩm ngẫu nhiên
                if random.random() < 0.3:  # 30% xác suất thêm thumbnail thứ hai
                    image_name2 = random.choice(sample_image_names)
                    while image_name2 == image_name:  # Đảm bảo không trùng tên
                        image_name2 = random.choice(sample_image_names)
                        
                    path_to_thumbnail2 = f"/static/thumbnails/{product.code}_alt_{image_name2}" if product.code else f"/static/thumbnails/product_{product.id}_alt_{image_name2}"
                    
                    thumbnail2 = Thumbnail(
                        type_detail_id=product.id,
                        path_to_thumbnail=path_to_thumbnail2
                    )
                    db.add(thumbnail2)
                    thumbnails_added += 1
        
        db.commit()
        print(f"Đã thêm {thumbnails_added} thumbnail cho các sản phẩm.")
        
        # Hiển thị một số thống kê
        products_with_thumbnails = db.query(TypeDetail).join(Thumbnail).distinct().count()
        total_thumbnails = db.query(Thumbnail).count()
        
        print(f"Số sản phẩm có thumbnail: {products_with_thumbnails}/{len(products)}")
        print(f"Tổng số thumbnail: {total_thumbnails}")
        
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi thêm thumbnail: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    try:
        print("Bắt đầu khởi tạo database...")
        init_db()
        # seed_data()
        # seed_paint_type()
        # seed_image()
        # seed_product_images()
        # seed_type_detail()
        # seed_order_detail()
        # seed_token_store()
        # seed_thumbnail_data()
        print("Khởi tạo database hoàn tất!")
    except Exception as e:
        print(f"Lỗi: {e}")
        traceback.print_exc()