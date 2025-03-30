import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router

# Tạo ứng dụng FastAPI
app = FastAPI(
    title="Paint App API",
    description="API cho ứng dụng bán sơn",
    version="1.0.0",

)

# Cấu hình CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8086",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm router cho API v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với API ứng dụng bán sơn"}

# Định nghĩa đường dẫn thư mục static
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
os.makedirs(static_dir, exist_ok=True)

# Thêm vào sau khi tạo ứng dụng FastAPI
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/admin-login")
def admin_login_page():
    return FileResponse(os.path.join(static_dir, "admin_login.html"))

@app.get("/admin")
def admin_page():
    return FileResponse(os.path.join(static_dir, "admin.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# 