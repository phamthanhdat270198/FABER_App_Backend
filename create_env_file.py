import os
import secrets

# Tạo SECRET_KEY mới
SECRET_KEY = secrets.token_hex(32)

# Đường dẫn đến file .env
ENV_FILE_PATH = ".env"

# Kiểm tra xem file .env đã tồn tại chưa
if os.path.exists(ENV_FILE_PATH):
    print(f"File {ENV_FILE_PATH} đã tồn tại.")
    overwrite = input("Bạn có muốn ghi đè không? (y/n): ")
    if overwrite.lower() != 'y':
        print("Hủy thao tác.")
        exit()

# Nội dung cho file .env
env_content = f"""# Cấu hình cơ bản
DEBUG=True
APP_NAME="Faber API"
API_PREFIX="/api/v1"

# Bảo mật
SECRET_KEY={SECRET_KEY}

# Database
DATABASE_URL=sqlite:///./sqlite_data/app.db

# JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logs
LOG_LEVEL=INFO
"""

# Ghi nội dung vào file .env
with open(ENV_FILE_PATH, "w", encoding='utf-8') as f:
    f.write(env_content)

print(f"Đã tạo file {ENV_FILE_PATH} với SECRET_KEY mới.")
print(f"SECRET_KEY: {SECRET_KEY}")