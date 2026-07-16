import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_platform_admin
from app.crud import crud_platform_admin
from app.models.user import User, UserRole
from app.schemas.platform_admin import (
    PlatformAdminPasswordReset,
    PlatformAdminUserCreate,
    PlatformAdminUserPublic,
    PlatformAdminUserUpdate,
)

router = APIRouter(prefix="/platform-admin", tags=["platform-admin"])


@router.get("/users", response_model=list[PlatformAdminUserPublic])
def list_users(
    search: Optional[str] = Query(None, description="Suche nach Name oder E-Mail"),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
) -> list[PlatformAdminUserPublic]:
    return crud_platform_admin.list_users(db, search=search, role=role, is_active=is_active)


@router.post("/users", response_model=PlatformAdminUserPublic, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: PlatformAdminUserCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
) -> PlatformAdminUserPublic:
    from app.crud.crud_user import get_by_email
    if get_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Diese E-Mail-Adresse ist bereits vergeben.",
        )
    return crud_platform_admin.create_user(db, payload)


@router.get("/users/{user_id}", response_model=PlatformAdminUserPublic)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
) -> PlatformAdminUserPublic:
    user = crud_platform_admin.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden.")
    return crud_platform_admin._to_public(db, user)


@router.patch("/users/{user_id}", response_model=PlatformAdminUserPublic)
def update_user(
    user_id: uuid.UUID,
    payload: PlatformAdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_platform_admin),
) -> PlatformAdminUserPublic:
    user = crud_platform_admin.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden.")
    # Self-protection: platform_admin cannot remove own role
    if user.id == admin.id and payload.role is not None and payload.role != UserRole.platform_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Du kannst dir selbst nicht die Platform-Admin-Rolle entziehen.",
        )
    if user.id == admin.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Du kannst dein eigenes Konto nicht deaktivieren.",
        )
    return crud_platform_admin.update_user(db, user, payload, admin.id)


@router.post("/users/{user_id}/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    user_id: uuid.UUID,
    payload: PlatformAdminPasswordReset,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_platform_admin),
) -> dict:
    user = crud_platform_admin.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden.")
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die Passwörter stimmen nicht überein.",
        )
    crud_platform_admin.reset_password(db, user, payload.new_password)
    return {"message": "Das Passwort wurde erfolgreich zurückgesetzt."}


@router.post("/users/{user_id}/activate", response_model=PlatformAdminUserPublic)
def activate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_platform_admin),
) -> PlatformAdminUserPublic:
    user = crud_platform_admin.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden.")
    return crud_platform_admin.set_active(db, user, True)


@router.post("/users/{user_id}/deactivate", response_model=PlatformAdminUserPublic)
def deactivate_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_platform_admin),
) -> PlatformAdminUserPublic:
    user = crud_platform_admin.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benutzer nicht gefunden.")
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Du kannst dein eigenes Konto nicht deaktivieren.",
        )
    return crud_platform_admin.set_active(db, user, False)
