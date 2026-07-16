import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field

from app.models.user import UserRole


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_active: bool
    voice_mode_enabled: bool
    onboarding_completed_at: Optional[datetime] = None
    first_login_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None

    @computed_field
    @property
    def needs_onboarding(self) -> bool:
        return self.onboarding_completed_at is None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        return f"{self.first_name[0]}{self.last_name[0]}".upper()


class LoginRequest(BaseModel):
    email: str
    password: str
