import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.user import UserRole


class PlatformAdminUserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    created_at: datetime
    first_login_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    onboarding_completed_at: Optional[datetime] = None
    organization_id: Optional[uuid.UUID] = None
    organization_name: Optional[str] = None


class PlatformAdminUserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: UserRole
    phone: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[uuid.UUID] = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Das Passwort muss mindestens 10 Zeichen lang sein.")
        return v


class PlatformAdminUserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    organization_id: Optional[uuid.UUID] = None


class PlatformAdminPasswordReset(BaseModel):
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Das Passwort muss mindestens 10 Zeichen lang sein.")
        return v
