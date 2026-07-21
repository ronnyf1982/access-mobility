import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.passenger_contact import ContactType


class PassengerContactBase(BaseModel):
    """Read/public schema — phone_number nullable for backward compat with existing DB rows."""
    name: str
    phone_number: str | None = None
    role_label: str | None = None
    contact_type: ContactType = ContactType.other
    note: str | None = None
    is_emergency_contact: bool = False
    visible_to_driver: bool = False
    visible_in_emergency: bool = False
    callable_in_emergency: bool = False
    priority: int = 1


class PassengerContactCreate(BaseModel):
    """Create schema — name AND phone_number are required and must be non-blank."""
    name: str
    phone_number: str
    role_label: str | None = None
    contact_type: ContactType = ContactType.other
    note: str | None = None
    is_emergency_contact: bool = False
    visible_to_driver: bool = False
    visible_in_emergency: bool = False
    callable_in_emergency: bool = False
    priority: int = 1

    @field_validator("name", "phone_number")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Darf nicht leer sein.")
        return v


class PassengerContactUpdate(BaseModel):
    """Update schema — all optional; empty strings and null for name/phone are rejected."""
    name: str | None = None
    phone_number: str | None = None
    role_label: str | None = None
    contact_type: ContactType | None = None
    note: str | None = None
    is_emergency_contact: bool | None = None
    visible_to_driver: bool | None = None
    visible_in_emergency: bool | None = None
    callable_in_emergency: bool | None = None
    priority: int | None = None

    @field_validator("name", "phone_number", mode="before")
    @classmethod
    def no_blank_or_null(cls, v: object) -> object:
        if v is None:
            raise ValueError("Darf nicht auf leer oder null gesetzt werden.")
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Darf nicht leer sein.")
        return v


class PassengerContactPublic(PassengerContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mobility_profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
