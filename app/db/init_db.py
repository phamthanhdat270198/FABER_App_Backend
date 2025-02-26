from sqlalchemy.orm import Session

from app.db.base import engine
from app.models.user import Base, User

# Tạo tất cả các bảng trong database
def init_db():
    Base.metadata.create_all(bind=engine)

# Nếu bạn muốn thêm dữ liệu mẫu
def seed_data(db: Session):
    # Kiểm tra xem đã có dữ liệu chưa
    user_count = db.query(User).count()
    if user_count == 0:
        # Thêm một số dữ liệu mẫu
        sample_users = [
            User(
                ho_ten="Nguyễn Văn A", 
                dia_chi="123 Đường Lê Lợi, Quận 1, TP.HCM", 
                so_dien_thoai="0901234567", 
                diem_thuong=100
            ),
            User(
                ho_ten="Trần Thị B", 
                dia_chi="456 Đường Nguyễn Huệ, Quận 1, TP.HCM", 
                so_dien_thoai="0912345678", 
                diem_thuong=150
            ),
        ]
        db.add_all(sample_users)
        db.commit()
        print("Đã thêm dữ liệu mẫu vào bảng users")

if __name__ == "__main__":
    # Tạo bảng khi chạy trực tiếp file này
    init_db()
    # Thêm dữ liệu mẫu
    db = Session(engine)
    seed_data(db)
    db.close()