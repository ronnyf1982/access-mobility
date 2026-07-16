from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.preview_access import PreviewAccessUser
from app.core.security import hash_password, verify_password
from app.schemas.preview_access import PreviewAccessUserCreate, PreviewAccessUserUpdate, PreviewAccessPasswordReset


def get_by_email(db: Session, email: str) -> PreviewAccessUser | None:
    return db.query(PreviewAccessUser).filter(PreviewAccessUser.email == email.strip().lower()).first()


def get_by_id(db: Session, user_id: int) -> PreviewAccessUser | None:
    return db.query(PreviewAccessUser).filter(PreviewAccessUser.id == user_id).first()


def list_users(db: Session, search: str | None = None, is_active: bool | None = None) -> list[PreviewAccessUser]:
    q = db.query(PreviewAccessUser)
    if search:
        term = f"%{search}%"
        q = q.filter(or_(
            PreviewAccessUser.email.ilike(term),
            PreviewAccessUser.first_name.ilike(term),
            PreviewAccessUser.last_name.ilike(term),
        ))
    if is_active is not None:
        q = q.filter(PreviewAccessUser.is_active == is_active)
    return q.order_by(PreviewAccessUser.created_at.desc()).all()


def create_user(db: Session, payload: PreviewAccessUserCreate) -> PreviewAccessUser:
    user = PreviewAccessUser(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        is_active=payload.is_active,
        note=payload.note,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: PreviewAccessUser, payload: PreviewAccessUserUpdate) -> PreviewAccessUser:
    update_data = payload.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(user, k, v)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def reset_password(db: Session, user: PreviewAccessUser, payload: PreviewAccessPasswordReset) -> None:
    user.password_hash = hash_password(payload.new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()


def set_active(db: Session, user: PreviewAccessUser, active: bool) -> PreviewAccessUser:
    user.is_active = active
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def validate_login(db: Session, email_or_username: str, password: str) -> PreviewAccessUser | None:
    """Returns user if credentials valid and active, else None."""
    user = get_by_email(db, email_or_username)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    user.last_used_at = datetime.now(timezone.utc)
    db.commit()
    return user
