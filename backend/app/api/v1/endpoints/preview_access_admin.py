from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_platform_admin
from app.crud import crud_preview_access
from app.models.user import User
from app.schemas.preview_access import (
    PreviewAccessUserPublic,
    PreviewAccessUserCreate,
    PreviewAccessUserUpdate,
    PreviewAccessPasswordReset,
)

router = APIRouter(prefix="/platform-admin/test-access-users", tags=["platform-admin"])


@router.get("", response_model=list[PreviewAccessUserPublic])
def list_preview_users(
    search: str | None = Query(None),
    is_active: bool | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> list:
    return crud_preview_access.list_users(db, search=search, is_active=is_active)


@router.post("", response_model=PreviewAccessUserPublic, status_code=201)
def create_preview_user(
    payload: PreviewAccessUserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> object:
    existing = crud_preview_access.get_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Diese E-Mail-Adresse ist bereits vergeben.")
    return crud_preview_access.create_user(db, payload)


@router.get("/{user_id}", response_model=PreviewAccessUserPublic)
def get_preview_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> object:
    user = crud_preview_access.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Zugang nicht gefunden.")
    return user


@router.patch("/{user_id}", response_model=PreviewAccessUserPublic)
def update_preview_user(
    user_id: int,
    payload: PreviewAccessUserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> object:
    user = crud_preview_access.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Zugang nicht gefunden.")
    return crud_preview_access.update_user(db, user, payload)


@router.post("/{user_id}/activate", response_model=PreviewAccessUserPublic)
def activate_preview_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> object:
    user = crud_preview_access.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Zugang nicht gefunden.")
    return crud_preview_access.set_active(db, user, True)


@router.post("/{user_id}/deactivate", response_model=PreviewAccessUserPublic)
def deactivate_preview_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> object:
    user = crud_preview_access.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Zugang nicht gefunden.")
    return crud_preview_access.set_active(db, user, False)


@router.post("/{user_id}/reset-password")
def reset_preview_user_password(
    user_id: int,
    payload: PreviewAccessPasswordReset,
    db: Session = Depends(get_db),
    _: User = Depends(require_platform_admin),
) -> dict:
    user = crud_preview_access.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Zugang nicht gefunden.")
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="Passwörter stimmen nicht überein.")
    crud_preview_access.reset_password(db, user, payload)
    return {"ok": True}
