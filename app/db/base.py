import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tạo thư mục sqlite_data nếu chưa tồn tại
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_DIR = os.path.join(BASE_DIR, "sqlite_data")
os.makedirs(DATABASE_DIR, exist_ok=True)

# Sử dụng đường dẫn tuyệt đối
DATABASE_PATH = os.path.join(DATABASE_DIR, "app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Hiển thị đường dẫn để debug
print(f"Database path: {DATABASE_PATH}")

# Tạo engine kết nối
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Hàm để tạo session khi cần
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
