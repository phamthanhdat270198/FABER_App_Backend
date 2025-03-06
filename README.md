
# FABER_App Backend

Dự án này là backend cho ứng dụng FABER_App, được xây dựng bằng Python FastApi + Sqlite.

## Hướng dẫn cài đặt và chạy

1.  **Clone dự án:**

    ```bash
    git clone [https://github.com/phamthanhdat270198/FABER_App_Backend.git](https://github.com/phamthanhdat270198/FABER_App_Backend.git)
    ```

2.  **Tạo môi trường ảo (virtual environment):**

    * Nếu bạn chưa cài đặt Python, hãy tải xuống từ [python.org](https://www.python.org/).
    * Di chuyển đến thư mục dự án:

        ```bash
        cd FABER_App_Backend
        ```

    * Tạo môi trường ảo:

        ```bash
        python -m venv venv
        ```

    * Kích hoạt môi trường ảo:

        ```bash
        venv\Scripts\activate # Trên Windows
        # source venv/bin/activate # Trên macOS/Linux
        ```

3.  **Cài đặt các gói phụ thuộc:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Chạy ứng dụng:**

    * Chạy ứng dụng chính:

        ```bash
        python -m app.main
        ```

    * Chạy script để trực quan hóa cơ sở dữ liệu người dùng:

        ```bash
        python -m app.scripts.visualize_db
        ```

## Các lệnh bổ sung

* `python -m app.scripts.visualize_db`: Chạy script để trực quan hóa cơ sở dữ liệu người dùng.
* Để hiển thị chi tiết từng bảng trong cơ sở dữ liệu. Uncomment các lệnh chạy trong hàm main của visualize_db.py
* Trong folder app.scripts còn có các ví dụ để thay đổi cấu trúc dữ liệu như add_colum_user.py, change_uuid_id.py. Lệnh chạy `python -m app.scripts.add_colum_user`

## Yêu cầu

* Python 3.13.2 (đang sử dụng hiện tại)
* Các gói phụ thuộc được liệt kê trong `requirements.txt`.

## Đóng góp

Nếu bạn muốn đóng góp cho dự án này, vui lòng fork repository và gửi pull request.

## Liên hệ

* [phamthanhdat270198@gmail.com](mailto:phamthanhdat270198@gmail.com)