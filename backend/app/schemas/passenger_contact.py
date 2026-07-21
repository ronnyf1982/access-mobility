import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.passenger_contact import ContactType


class PassengerContactBase(BaseModel):
    name: str
    phone_number: str | None = None
    role_label: str | None = None
    contact_type: ContactType = ContactType.other
    note: str | None = None
    is_emergency_contact: bool = False
    visible_to_driver: bool = False
    visible_in_emergency: bool = False
    callable_in_emergency: bool = False
    priority: int = 999


class PassengerContactCreate(PassengerContactBase):
    pass


class PassengerContactUpdate(BaseModel):
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


class PassengerContactPublic(PassengerContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mobility_profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
