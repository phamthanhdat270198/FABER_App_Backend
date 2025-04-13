from sqlalchemy import func  # Import func từ sqlalchemy
from app.db.base import SessionLocal  # Đảm bảo import SessionLocal từ module database của bạn
from app.models.user import User  # Đảm bảo import User từ module models của bạn
from tabulate import tabulate

def confirm_action(message):
    """Xác nhận hành động từ người dùng"""
    response = input(f"{message} (y/n): ").lower()
    return response == 'y'

def reset_all_kth_spin():
    """Reset kth_spin về 0 cho tất cả người dùng"""
    db = SessionLocal()
    try:
        # Lấy danh sách người dùng có kth_spin > 0
        users_with_spins = db.query(User).filter(User.kth_spin > 0).all()
        
        if not users_with_spins:
            print("Không có người dùng nào có kth_spin > 0.")
            return
        
        # Hiển thị danh sách người dùng sẽ bị reset
        print("\n=== RESET KTH_SPIN VỀ 0 CHO TẤT CẢ NGƯỜI DÙNG ===")
        print(f"Số lượng người dùng sẽ được reset: {len(users_with_spins)}")
        
        # Hiển thị thông tin người dùng sẽ bị reset
        headers = ["ID", "Họ tên", "Số điện thoại", "Điểm thưởng", "kth_spin hiện tại"]
        rows = []
        
        for user in users_with_spins:
            rows.append([
                user.id,
                user.ho_ten,
                user.so_dien_thoai if user.so_dien_thoai else "N/A",
                user.diem_thuong,
                user.kth_spin
            ])
        
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        
        # Yêu cầu xác nhận
        if not confirm_action("Bạn có chắc chắn muốn reset kth_spin về 0 cho tất cả người dùng không?"):
            print("Đã hủy thao tác reset.")
            return
        
        # Thực hiện reset
        updated_count = db.query(User).filter(User.kth_spin > 0).update({User.kth_spin: 0})
        db.commit()
        
        print(f"\nĐã reset kth_spin về 0 cho {updated_count} người dùng.")
        
    except Exception as e:
        db.rollback()
        print(f"Đã xảy ra lỗi khi reset kth_spin: {str(e)}")
    finally:
        db.close()

def reset_kth_spin_by_user():
    """Reset kth_spin về 0 cho người dùng cụ thể"""
    db = SessionLocal()
    try:
        # Lấy danh sách tất cả người dùng có kth_spin > 0
        users = db.query(User.id, User.ho_ten, User.kth_spin) \
                .filter(User.kth_spin > 0) \
                .order_by(User.kth_spin.desc()) \
                .all()
        
        if not users:
            print("Không có người dùng nào có kth_spin > 0.")
            return
        
        # Hiển thị danh sách người dùng
        print("\n=== RESET KTH_SPIN THEO NGƯỜI DÙNG ===")
        headers = ["ID", "Họ tên", "kth_spin hiện tại"]
        rows = [[user.id, user.ho_ten, user.kth_spin] for user in users]
        
        print(tabulate(rows, headers=headers, tablefmt="pretty"))
        
        # Yêu cầu nhập user_id để reset
        user_input = input("\nNhập User ID để reset kth_spin (nhập 'all' để reset tất cả, 'cancel' để hủy): ")
        
        if user_input.lower() == 'cancel':
            print("Đã hủy thao tác reset.")
            return
        elif user_input.lower() == 'all':
            reset_all_kth_spin()
            return
        
        try:
            user_id = int(user_input)
            
            # Kiểm tra user_id có hợp lệ không
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                print(f"Không tìm thấy người dùng với ID: {user_id}")
                return
            
            if user.kth_spin == 0:
                print(f"Người dùng với ID {user_id} đã có kth_spin = 0 rồi.")
                return
            
            # Hiển thị thông tin người dùng
            print(f"\nThông tin người dùng:")
            print(f"ID: {user.id}")
            print(f"Họ tên: {user.ho_ten}")
            print(f"kth_spin hiện tại: {user.kth_spin}")
            
            # Yêu cầu xác nhận
            if not confirm_action(f"Bạn có chắc chắn muốn reset kth_spin về 0 cho người dùng này không?"):
                print("Đã hủy thao tác reset.")
                return
            
            # Thực hiện reset
            user.kth_spin = 0
            db.commit()
            
            print(f"\nĐã reset kth_spin về 0 cho người dùng {user.ho_ten} (ID: {user.id}).")
            
        except ValueError:
            print("User ID không hợp lệ. Vui lòng nhập số nguyên.")
            return
        
    except Exception as e:
        db.rollback()
        print(f"Đã xảy ra lỗi khi reset kth_spin: {str(e)}")
    finally:
        db.close()

def show_kth_spin_statistics():
    """Hiển thị thống kê về kth_spin"""
    db = SessionLocal()
    try:
        # Lấy tổng số người dùng
        total_users = db.query(User).count()
        
        # Lấy số người dùng có kth_spin > 0
        users_with_spins = db.query(User).filter(User.kth_spin > 0).count()
        
        # Lấy giá trị kth_spin lớn nhất, nhỏ nhất và trung bình
        # Sử dụng func từ sqlalchemy, không phải từ session
        max_spin = db.query(func.max(User.kth_spin)).scalar() or 0
        min_spin = db.query(func.min(User.kth_spin)).scalar() or 0
        avg_spin = db.query(func.avg(User.kth_spin)).scalar() or 0
        
        # Lấy phân phối kth_spin
        spin_distribution = db.query(User.kth_spin, func.count(User.id)) \
                           .group_by(User.kth_spin) \
                           .order_by(User.kth_spin) \
                           .all()
        
        # Hiển thị thống kê
        print("\n=== THỐNG KÊ KTH_SPIN ===")
        stats = [
            ["Tổng số người dùng", total_users],
            ["Số người dùng có kth_spin > 0", users_with_spins],
            ["Tỷ lệ người dùng có kth_spin > 0", f"{(users_with_spins / total_users) * 100:.2f}%" if total_users > 0 else "0%"],
            ["kth_spin lớn nhất", max_spin],
            ["kth_spin nhỏ nhất", min_spin],
            ["kth_spin trung bình", f"{avg_spin:.2f}"]
        ]
        
        print(tabulate(stats, headers=["Chỉ số", "Giá trị"], tablefmt="pretty"))
        
        # Hiển thị phân phối kth_spin
        print("\nPhân phối kth_spin:")
        dist_headers = ["kth_spin", "Số lượng người dùng"]
        dist_rows = [[spin, count] for spin, count in spin_distribution]
        
        print(tabulate(dist_rows, headers=dist_headers, tablefmt="pretty"))
        
    except Exception as e:
        print(f"Đã xảy ra lỗi khi lấy thống kê: {str(e)}")
    finally:
        db.close()

def main():
    """Hàm chính"""
    print("=" * 50)
    print("CÔNG CỤ RESET KTH_SPIN TRONG BẢNG USER")
    print("=" * 50)
    
    while True:
        print("\nCác chức năng:")
        print("1. Reset kth_spin về 0 cho tất cả người dùng")
        print("2. Reset kth_spin về 0 cho người dùng cụ thể")
        print("3. Xem thống kê về kth_spin")
        print("0. Thoát")
        
        choice = input("\nChọn chức năng (0-3): ")
        
        if choice == '1':
            reset_all_kth_spin()
        elif choice == '2':
            reset_kth_spin_by_user()
        elif choice == '3':
            show_kth_spin_statistics()
        elif choice == '0':
            print("\nĐã thoát chương trình.")
            break
        else:
            print("\nLựa chọn không hợp lệ. Vui lòng chọn lại.")

if __name__ == "__main__":
    main()