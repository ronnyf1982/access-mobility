import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.mobility_profile import WheelchairType


class MobilityProfileBase(BaseModel):
    display_name: str | None = None
    date_of_birth: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    uses_wheelchair: bool = False
    wheelchair_type: WheelchairType | None = None
    uses_rollator: bool = False
    uses_crutches: bool = False
    is_blind_or_visually_impaired: bool = False
    is_deaf_or_hard_of_hearing: bool = False
    needs_escort: bool = False
    needs_entry_assistance: bool = False
    needs_door_to_door_assistance: bool = False
    needs_ramp: bool = False
    needs_lift: bool = False
    needs_stretcher_transport: bool = False

    can_transfer_to_seat: bool | None = None
    has_own_wheelchair: bool | None = None
    requires_wheelchair_space: bool = False
    requires_extra_time: bool = False

    communication_notes: str | None = None
    medical_notes: str | None = None
    general_notes: str | None = None


class MobilityProfileCreate(MobilityProfileBase):
    pass


class MobilityProfileUpdate(BaseModel):
    """Partielle Updates — nur gesendete Felder werden geschrieben."""

    display_name: str | None = None
    date_of_birth: str | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None

    uses_wheelchair: bool | None = None
    wheelchair_type: WheelchairType | None = None
    uses_rollator: bool | None = None
    uses_crutches: bool | None = None
    is_blind_or_visually_impaired: bool | None = None
    is_deaf_or_hard_of_hearing: bool | None = None
    needs_escort: bool | None = None
    needs_entry_assistance: bool | None = None
    needs_door_to_door_assistance: bool | None = None
    needs_ramp: bool | None = None
    needs_lift: bool | None = None
    needs_stretcher_transport: bool | None = None

    can_transfer_to_seat: bool | None = None
    has_own_wheelchair: bool | None = None
    requires_wheelchair_space: bool | None = None
    requires_extra_time: bool | None = None

    communication_notes: str | None = None
    medical_notes: str | None = None
    general_notes: str | None = None


class MobilityProfilePublic(MobilityProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
