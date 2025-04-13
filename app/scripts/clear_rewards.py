from app.db.base import SessionLocal
from app.models.rewards_spin import SpinReward
import os
from tabulate import tabulate

def confirm_action(message):
    """Xác nhận hành động từ người dùng"""
    response = input(f"{message} (y/n): ").lower()
    return response == 'y'

def clear_all_spin_rewards():
    """Xóa tất cả dữ liệu trong bảng spin_rewards"""
    db = SessionLocal()
    try:
        # Đếm số lượng bản ghi trước khi xóa
        count = db.query(SpinReward).count()
        
        if count == 0:
            print("Bảng spin_rewards không có dữ liệu để xóa.")
            return
        
        # Hiển thị số lượng bản ghi sẽ bị xóa
        print(f"\n=== XÓA DỮ LIỆU BẢNG SPIN_REWARDS ===")
        print(f"Số lượng bản ghi sẽ bị xóa: {count}")
        
        # Hiển thị mẫu dữ liệu sắp xóa
        sample_data = db.query(SpinReward).limit(5).all()
        
        if sample_data:
            print("\nMẫu dữ liệu sẽ bị xóa:")
            headers = ["ID", "User ID", "Loại phần quà", "Đã nhận", "Lần quay thứ", "Ngày tạo"]
            rows = []
            
            for reward in sample_data:
                claimed_status = "Đã nhận" if reward.is_claimed else "Chưa nhận"
                
                rows.append([
                    reward.id,
                    reward.user_id,
                    reward.reward_type,
                    claimed_status,
                    reward.spin_number,
                    reward.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(reward, 'created_at') and reward.created_at else "N/A"
                ])
            
            print(tabulate(rows, headers=headers, tablefmt="pretty"))
            if count > 5:
                print(f"... và {count - 5} bản ghi khác")
        
        # Yêu cầu xác nhận
        if not confirm_action("Bạn có chắc chắn muốn xóa TẤT CẢ dữ liệu trong bảng spin_rewards không?"):
            print("Đã hủy thao tác xóa dữ liệu.")
            return
        
        # Yêu cầu xác nhận lần 2 để tránh nhầm lẫn
        if not confirm_action("CẢNH BÁO: Dữ liệu đã xóa không thể khôi phục. Xác nhận lần cuối?"):
            print("Đã hủy thao tác xóa dữ liệu.")
            return
        
        # Thực hiện xóa dữ liệu
        db.query(SpinReward).delete()
        db.commit()
        
        print(f"\nĐã xóa thành công {count} bản ghi từ bảng spin_rewards.")
        
    except Exception as e:
        db.rollback()
        print(f"Đã xảy ra lỗi khi xóa dữ liệu: {str(e)}")
    finally:
        db.close()



if __name__ == "__main__":
    clear_all_spin_rewards()