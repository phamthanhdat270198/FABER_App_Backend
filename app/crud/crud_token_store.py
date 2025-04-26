from typing import Optional, List
from datetime import datetime
import secrets
from sqlalchemy.orm import Session

from app.models.token_store import TokenStore
from app.schemas.token_store import TokenStoreCreate



def create_token(db: Session, user_id: int, expires_days: int = 30, device_info: Optional[str] = None) -> TokenStore:
    """
    Tạo token mới cho người dùng
    """
    # Tạo token ngẫu nhiên
    token = secrets.token_hex(32)  # 64 ký tự hex
    
    # Tạo bản ghi TokenStore
    db_token = TokenStore.create_for_user(
        user_id=user_id,
        token=token,
        expires_days=expires_days,
        device_info=device_info
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def create_token_no_remember(db: Session, user_id: int, expires_days: int = 60*24, device_info: Optional[str] = None) -> TokenStore:
    """
    Tạo token mới cho người dùng
    """
    # Tạo token ngẫu nhiên
    token = secrets.token_hex(32)  # 64 ký tự hex
    
    # Tạo bản ghi TokenStore
    db_token = TokenStore.create_for_user_no_remember(
        user_id=user_id,
        token=token,
        expires_days=expires_days,
        device_info=device_info
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_by_token(db: Session, token: str) -> Optional[TokenStore]:
    """
    Lấy bản ghi token từ chuỗi token
    """
    return db.query(TokenStore).filter(TokenStore.token == token).first()

def get_valid_tokens_for_user(db: Session, user_id: int) -> List[TokenStore]:
    """
    Lấy tất cả token hợp lệ của một người dùng
    """
    now = datetime.utcnow()
    return (
        db.query(TokenStore)
        .filter(
            TokenStore.user_id == user_id,
            TokenStore.expires_at > now,
            TokenStore.is_revoked == False
        )
        .all()
    )

def revoke_token(db: Session, token: str) -> bool:
    """
    Thu hồi token (đăng xuất)
    """
    db_token = get_by_token(db, token)
    if not db_token:
        return False
    
    db_token.is_revoked = True
    db.add(db_token)
    db.commit()
    return True

def revoke_all_tokens_for_user(db: Session, user_id: int) -> int:
    """
    Thu hồi tất cả token của người dùng (đăng xuất khỏi tất cả thiết bị)
    """
    tokens = get_valid_tokens_for_user(db, user_id)
    count = 0
    
    for token in tokens:
        token.is_revoked = True
        db.add(token)
        count += 1
    
    db.commit()
    return count

def update_last_used(db: Session, db_token: TokenStore) -> TokenStore:
    """
    Cập nhật thời gian sử dụng gần nhất của token
    """
    db_token.last_used_at = datetime.utcnow()
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def clean_expired_tokens(db: Session) -> int:
    """
    Dọn dẹp các token đã hết hạn (có thể chạy như một tác vụ định kỳ)
    """
    now = datetime.utcnow()
    expired = db.query(TokenStore).filter(TokenStore.expires_at < now).delete()
    db.commit()
    return expired