from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path, status, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.base import get_db
from app.models.paint_type import PaintType
from app.schemas.paint_type import PaintTypeCreate, PaintTypeUpdate, PaintTypeResponse
from app.api.deps import get_current_admin_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[PaintTypeResponse])
def get_all_paint_types(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Lấy danh sách tất cả các loại sơn.
    """
    paint_types = db.query(PaintType).offset(skip).limit(limit).all()
    return paint_types

@router.post("", response_model=PaintTypeResponse, status_code=status.HTTP_201_CREATED)
# @router.post("", response_model=PaintTypeResponse, status_code=status.HTTP_201_CREATED)
def create_paint_type(
    *,
    db: Session = Depends(get_db),
    paint_type_in: PaintTypeCreate,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Tạo loại sơn mới.
    Chỉ admin mới có quyền thực hiện.
    """
    try:
        # Kiểm tra xem paint_type đã tồn tại chưa
        existing = db.query(PaintType).filter(PaintType.paint_type == paint_type_in.paint_type).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loại sơn này đã tồn tại"
            )
        
        # Tạo loại sơn mới
        db_obj = PaintType(
            paint_type=paint_type_in.paint_type,
            mo_ta_san_pham=paint_type_in.mo_ta_san_pham,
            thanh_phan=paint_type_in.thanh_phan,
            huong_dan_su_dung=paint_type_in.huong_dan_su_dung,
            luu_y=paint_type_in.luu_y,
            bao_quan=paint_type_in.bao_quan
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)  # Đảm bảo ID đã được tạo
        return db_obj
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lỗi toàn vẹn dữ liệu, vui lòng kiểm tra lại thông tin"
        )

@router.get("/{paint_type_id}", response_model=PaintTypeResponse)
def get_paint_type(
    paint_type_id: int = Path(..., title="ID của loại sơn", ge=1),
    db: Session = Depends(get_db)
) -> Any:
    """
    Lấy thông tin chi tiết của một loại sơn theo ID.
    """
    paint_type = db.query(PaintType).filter(PaintType.id == paint_type_id).first()
    if not paint_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sơn"
        )
    print("get id ------------ ")
    return paint_type

@router.put("/{paint_type_id}", response_model=PaintTypeResponse)
def update_paint_type(
    *,
    db: Session = Depends(get_db),
    paint_type_id: int = Path(..., title="ID của loại sơn", ge=1),
    paint_type_in: PaintTypeUpdate,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Cập nhật thông tin loại sơn.
    Chỉ admin mới có quyền thực hiện.
    """
    paint_type = db.query(PaintType).filter(PaintType.id == paint_type_id).first()
    if not paint_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sơn"
        )
    
    try:
        # Cập nhật thông tin
        update_data = paint_type_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(paint_type, field, update_data[field])
        
        db.add(paint_type)
        db.commit()
        db.refresh(paint_type)
        print("put ---------------")
        return paint_type
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lỗi toàn vẹn dữ liệu, có thể tên loại sơn đã tồn tại"
        )

@router.delete("/{paint_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paint_type(
    *,
    db: Session = Depends(get_db),
    paint_type_id: int = Path(..., title="ID của loại sơn", ge=1),
    current_user: User = Depends(get_current_admin_user)
) -> None:  # Thay đổi kiểu trả về thành None
    """
    Xóa một loại sơn.
    Chỉ admin mới có quyền thực hiện.
    Chú ý: Xóa loại sơn sẽ xóa cả các sản phẩm liên quan.
    """
    paint_type = db.query(PaintType).filter(PaintType.id == paint_type_id).first()
    if not paint_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sơn"
        )
    
    try:
        # Kiểm tra xem có sản phẩm nào liên quan không
        if paint_type.type_details and len(paint_type.type_details) > 0:
            # Có thể bỏ comment dòng dưới nếu muốn ngăn xóa khi có sản phẩm liên quan
            # raise HTTPException(status_code=400, detail=f"Không thể xóa vì có {len(paint_type.type_details)} sản phẩm liên quan")
            
            # Hoặc hiển thị cảnh báo trong log
            print(f"Cảnh báo: Xóa loại sơn ID={paint_type_id} sẽ xóa {len(paint_type.type_details)} sản phẩm liên quan")
        
        # Thực hiện xóa
        db.delete(paint_type)
        db.commit()
        # Không trả về gì cả
        return None
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi xóa loại sơn: {str(e)}"
        )
    
@router.post("/with-id/{custom_id}", response_model=PaintTypeResponse, status_code=status.HTTP_201_CREATED)
def create_paint_type_with_custom_id(
    *,
    db: Session = Depends(get_db),
    custom_id: int = Path(..., title="ID tùy chỉnh", ge=1),
    paint_type_in: PaintTypeCreate,
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Tạo loại sơn mới với ID tùy chỉnh.
    Chỉ admin mới có quyền thực hiện.
    """
    try:
        # Kiểm tra xem ID đã tồn tại chưa
        existing_id = db.query(PaintType).filter(PaintType.id == custom_id).first()
        if existing_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ID {custom_id} đã tồn tại trong database"
            )
        
        # Kiểm tra xem paint_type đã tồn tại chưa
        existing_name = db.query(PaintType).filter(PaintType.paint_type == paint_type_in.paint_type).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Loại sơn này đã tồn tại"
            )
        
        # Tạo loại sơn mới với ID tùy chỉnh
        db_obj = PaintType(
            id=custom_id,
            paint_type=paint_type_in.paint_type,
            mo_ta_san_pham=paint_type_in.mo_ta_san_pham,
            thanh_phan=paint_type_in.thanh_phan,
            huong_dan_su_dung=paint_type_in.huong_dan_su_dung,
            luu_y=paint_type_in.luu_y,
            bao_quan=paint_type_in.bao_quan
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Lỗi toàn vẹn dữ liệu, vui lòng kiểm tra lại thông tin"
        )
    
@router.patch("/{paint_type_id}/toggle-active", response_model=PaintTypeResponse)
def toggle_paint_type_active(
    paint_type_id: int = Path(..., title="ID của loại sơn", ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
) -> Any:
    """
    Bật/tắt trạng thái hoạt động của loại sơn
    """
    paint_type = db.query(PaintType).filter(PaintType.id == paint_type_id).first()
    if not paint_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy loại sơn"
        )
    
    # Đảo ngược trạng thái
    paint_type.is_active = not paint_type.is_active
    
    db.add(paint_type)
    db.commit()
    db.refresh(paint_type)
    
    return paint_type