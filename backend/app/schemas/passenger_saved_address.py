import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.passenger_saved_address import AddressType


class PassengerSavedAddressBase(BaseModel):
    label: str
    address_type: AddressType = AddressType.other
    street_address: str
    postal_code: str
    city: str
    additional_info: str | None = None
    note: str | None = None
    is_default_pickup: bool = False
    is_default_destination: bool = False
    is_active: bool = True


class PassengerSavedAddressCreate(PassengerSavedAddressBase):
    """Create schema — label, street_address, postal_code, city are required non-blank."""

    @field_validator("label", "street_address", "postal_code", "city")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Darf nicht leer sein.")
        return v


class PassengerSavedAddressUpdate(BaseModel):
    """Update schema — all optional; blank strings for required fields are rejected."""

    label: str | None = None
    address_type: AddressType | None = None
    street_address: str | None = None
    postal_code: str | None = None
    city: str | None = None
    additional_info: str | None = None
    note: str | None = None
    is_default_pickup: bool | None = None
    is_default_destination: bool | None = None
    is_active: bool | None = None

    @field_validator("label", "street_address", "postal_code", "city", mode="before")
    @classmethod
    def no_blank_if_sent(cls, v: object) -> object:
        if v is None:
            return v
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Darf nicht leer sein.")
        return v


class PassengerSavedAddressPublic(PassengerSavedAddressBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    mobility_profile_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
