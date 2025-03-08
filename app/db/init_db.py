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
from app.models.order import Order, OrderStatus
from app.models.paint_type import PaintType
from app.models.image_resource import ImageResource
from app.models.type_detail import TypeDetail
from app.models.order_detail import OrderDetail
from app.models.token_store import TokenStore
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
    paint_type_count = db.query(PaintType).count()
    if paint_type_count == 0:
        sample_paint_types = [
            PaintType(
                paint_type="Sơn Nước",
                description="Sơn dễ pha loãng, khô nhanh, ít mùi, dễ lau chùi, phù hợp cho tường trong nhà"
            ),
            PaintType(
                paint_type="Sơn Dầu",
                description="Sơn gốc dầu, bền màu, chống thấm tốt, phù hợp cho bề mặt kim loại và gỗ"
            ),
            PaintType(
                paint_type="Sơn Chống Rỉ",
                description="Sơn lót đặc biệt ngăn chặn quá trình oxy hóa, bảo vệ bề mặt kim loại"
            ),
            PaintType(
                paint_type="Sơn Epoxy",
                description="Sơn hai thành phần, độ bám dính và độ bền cao, chịu hóa chất, phù hợp cho sàn công nghiệp"
            ),
            PaintType(
                paint_type="Sơn Nội Thất",
                description="Sơn chuyên dụng cho không gian trong nhà, ít mùi, an toàn cho sức khỏe"
            ),
        ]
        db.add_all(sample_paint_types)
        db.commit()
        print("Đã thêm dữ liệu mẫu vào bảng paint_types")


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

if __name__ == "__main__":
    try:
        print("Bắt đầu khởi tạo database...")
        init_db()
        # seed_data()
        # seed_paint_type()
        # seed_image()
        # seed_type_detail()
        # seed_order_detail()
        seed_token_store()
        print("Khởi tạo database hoàn tất!")
    except Exception as e:
        print(f"Lỗi: {e}")
        traceback.print_exc()