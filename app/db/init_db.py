# app/db/init_db.py
import os
import sys
import uuid
from datetime import datetime, timedelta
import traceback

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
    img_path = r"C:\Users\THANH DAT\Pictures\faber_imgs"
    try:
        # Thêm dữ liệu mẫu cho image_resources
        image_count = db.query(ImageResource).count()
        if image_count == 0:
            sample_images = []
            for img_name in os.listdir(img_path):
                image_path = os.path.join(img_path, img_name)
                img_resource = ImageResource(
                    uuid=str(uuid.uuid4()),
                    image_path=image_path
                )
                sample_images.append(img_resource)
            # sample_images = [
            #     ImageResource(
            #         uuid=str(uuid.uuid4()),
            #         image_path="/uploads/images/product_001.jpg"
            #     ),
            #     ImageResource(
            #         uuid=str(uuid.uuid4()),
            #         image_path="/uploads/images/product_002.jpg"
            #     ),
            #     ImageResource(
            #         uuid=str(uuid.uuid4()),
            #         image_path="/uploads/images/banner_main.jpg"
            #     ),
            #     ImageResource(
            #         uuid=str(uuid.uuid4()),
            #         image_path="/uploads/images/gallery/interior_01.jpg"
            #     ),
            #     ImageResource(
            #         uuid=str(uuid.uuid4()),
            #         image_path="/uploads/images/gallery/exterior_02.jpg"
            #     ),
            # ]
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
if __name__ == "__main__":
    try:
        print("Bắt đầu khởi tạo database...")
        init_db()
        # seed_data()
        # seed_paint_type()
        # seed_image()
        seed_type_detail()
        print("Khởi tạo database hoàn tất!")
    except Exception as e:
        print(f"Lỗi: {e}")
        traceback.print_exc()