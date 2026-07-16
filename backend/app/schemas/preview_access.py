from datetime import datetime
from pydantic import BaseModel, field_validator


class PublicGateLoginRequest(BaseModel):
    email_or_username: str
    password: str


class PreviewAccessUserPublic(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    note: str | None
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PreviewAccessUserCreate(BaseModel):
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    note: str | None = None

    @field_validator('email')
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('Passwort muss mindestens 10 Zeichen haben.')
        return v


class PreviewAccessUserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    note: str | None = None


class PreviewAccessPasswordReset(BaseModel):
    new_password: str
    confirm_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError('Passwort muss mindestens 10 Zeichen haben.')
        return v
