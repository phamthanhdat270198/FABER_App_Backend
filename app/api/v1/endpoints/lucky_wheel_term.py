from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()
# Dữ liệu đơn giản dạng dict
terms_data = {
    "title": "QUY TẮC CHÍNH THỨC – VÒNG QUAY MAY MẮN",
    "content": [
        {
            "title": "1. Đối Tượng Tham Gia",
            "text": [
                "Chương trình Vòng quay may mắn chỉ áp dụng cho khách hàng đã mua hàng tại hệ thống của chúng tôi và tích đủ điểm để có lượt quay.",
                "Người tham gia phải đủ 18 tuổi trở lên, hoặc có sự đồng ý của phụ huynh/người giám hộ nếu dưới 18 tuổi.",
                "Nhân viên của công ty, đại lý hoặc đối tác trực tiếp tham gia tổ chức chương trình không được tham gia."
            ]
        },
        {
            "title": "2. Cách Thức Tham Gia",
            "text": [
                "Với mỗi giao dịch mua hàng hợp lệ, khách hàng sẽ được tích điểm.",
                "Khi đạt đủ số điểm quy định, khách hàng sẽ nhận được một lượt quay.",
                "Lượt quay có thể sử dụng trực tiếp tại điểm bán hoặc thông qua ứng dụng (nếu được hỗ trợ).",
                "Mỗi lượt quay chỉ có giá trị trong thời gian chương trình diễn ra.",
                "Việc tham gia chương trình đồng nghĩa với việc khách hàng đồng ý với toàn bộ Quy Tắc Chính Thức này."
            ]
        },
        {
            "title": "3. Giải Thưởng & Trao Giải",
            "text": [
                "Giải thưởng hoàn toàn ngẫu nhiên và tùy biến theo từng vòng quay.",
                "Tất cả giải thưởng được trao trực tiếp, không qua trung gian và không trao online.",
                "Giải thưởng không có giá trị quy đổi thành tiền mặt hoặc sản phẩm khác (trừ khi có quy định khác kèm theo).",
                "Để nhận giải, khách hàng liên hệ: https://sonfaber.com/lien-he/.",
                "Công ty không chịu trách nhiệm nếu khách hàng cung cấp thông tin liên hệ sai hoặc quá hạn nhận giải."
            ]
        },
        {
            "title": "4. Điều Khoản & Trách Nhiệm Pháp Lý",
            "text": [
                "Công ty có quyền điều chỉnh hoặc chấm dứt chương trình vào bất kỳ thời điểm nào mà không cần thông báo trước, trong trường hợp bất khả kháng hoặc vì lý do kỹ thuật.",
                "Mọi quyết định của công ty về kết quả vòng quay là cuối cùng và không có tranh chấp.",
                "Khi tham gia, khách hàng đồng ý cho phép công ty sử dụng tên và hình ảnh của mình cho mục đích quảng bá mà không phải trả thêm bất kỳ khoản chi phí nào.",
                "Apple không phải là nhà tài trợ, không có liên quan và không chịu trách nhiệm đối với chương trình này.",
                "Chương trình tuân thủ đầy đủ các quy định pháp luật hiện hành tại Việt Nam"
            ]
        }
    ]
}

@router.get("/terms")
def get_terms():
    return terms_data