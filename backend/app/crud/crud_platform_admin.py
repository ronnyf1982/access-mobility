import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.membership import OrganizationMembership
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.platform_admin import (
    PlatformAdminUserCreate,
    PlatformAdminUserPublic,
    PlatformAdminUserUpdate,
)


def _org_membership_for_user(db: Session, user_id: uuid.UUID) -> OrganizationMembership | None:
    return (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == user_id, OrganizationMembership.is_active == True)  # noqa: E712
        .first()
    )


def _to_public(db: Session, user: User) -> PlatformAdminUserPublic:
    membership = _org_membership_for_user(db, user.id)
    org_id = None
    org_name = None
    if membership:
        org = db.get(Organization, membership.organization_id)
        org_id = membership.organization_id
        org_name = org.name if org else None
    return PlatformAdminUserPublic(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        first_login_at=user.first_login_at,
        last_login_at=user.last_login_at,
        onboarding_completed_at=user.onboarding_completed_at,
        organization_id=org_id,
        organization_name=org_name,
    )


def list_users(
    db: Session,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
) -> list[PlatformAdminUserPublic]:
    q = db.query(User)
    if search:
        term = f"%{search.strip()}%"
        q = q.filter(
            (User.first_name.ilike(term))
            | (User.last_name.ilike(term))
            | (User.email.ilike(term))
        )
    if role is not None:
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    users = q.order_by(User.last_name, User.first_name).all()
    return [_to_public(db, u) for u in users]


def get_user(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, payload: PlatformAdminUserCreate) -> PlatformAdminUserPublic:
    now = datetime.now(timezone.utc)
    # Staff roles skip onboarding
    admin_roles = {
        UserRole.platform_admin,
        UserRole.provider_admin,
        UserRole.dispatcher,
        UserRole.organization_admin,
        UserRole.organization_coordinator,
        UserRole.driver,
        UserRole.trusted_person,
    }
    onboarding_at = now if payload.role in admin_roles else None

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        phone=payload.phone,
        role=payload.role,
        is_active=payload.is_active,
        onboarding_completed_at=onboarding_at,
    )
    db.add(user)
    db.flush()

    if payload.organization_id:
        _upsert_membership(db, user.id, payload.organization_id)

    db.commit()
    db.refresh(user)
    return _to_public(db, user)


def update_user(
    db: Session,
    user: User,
    payload: PlatformAdminUserUpdate,
    current_admin_id: uuid.UUID,
) -> PlatformAdminUserPublic:
    if payload.first_name is not None:
        user.first_name = payload.first_name.strip()
    if payload.last_name is not None:
        user.last_name = payload.last_name.strip()
    if payload.phone is not None:
        user.phone = payload.phone
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.organization_id is not None:
        _upsert_membership(db, user.id, payload.organization_id)

    db.commit()
    db.refresh(user)
    return _to_public(db, user)


def reset_password(db: Session, user: User, new_password: str) -> None:
    user.password_hash = hash_password(new_password)
    db.commit()


def set_active(db: Session, user: User, active: bool) -> PlatformAdminUserPublic:
    user.is_active = active
    db.commit()
    db.refresh(user)
    return _to_public(db, user)


def _upsert_membership(
    db: Session, user_id: uuid.UUID, organization_id: uuid.UUID
) -> None:
    existing = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == user_id)
        .first()
    )
    if existing:
        existing.organization_id = organization_id
        existing.is_active = True
    else:
        db.add(
            OrganizationMembership(
                user_id=user_id,
                organization_id=organization_id,
                organization_role="member",
                is_active=True,
            )
        )
