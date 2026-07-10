import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.mobility_profile import AttendantType, WheelchairType


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

    requires_transport_chair: bool = False
    requires_two_person_assistance: bool = False
    requires_medical_transport: bool = False
    brings_oxygen: bool = False
    requires_oxygen_mount: bool = False
    brings_medical_device: bool = False
    requires_medical_equipment_storage: bool = False
    requires_infusion_mount: bool = False
    requires_special_positioning: bool = False
    infection_or_hygiene_note: bool = False
    requires_medical_attendant: bool = False
    attendant_type_required: AttendantType = AttendantType.none
    medical_device_notes: str | None = None
    medical_transport_notes: str | None = None

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

    requires_transport_chair: bool | None = None
    requires_two_person_assistance: bool | None = None
    requires_medical_transport: bool | None = None
    brings_oxygen: bool | None = None
    requires_oxygen_mount: bool | None = None
    brings_medical_device: bool | None = None
    requires_medical_equipment_storage: bool | None = None
    requires_infusion_mount: bool | None = None
    requires_special_positioning: bool | None = None
    infection_or_hygiene_note: bool | None = None
    requires_medical_attendant: bool | None = None
    attendant_type_required: AttendantType | None = None
    medical_device_notes: str | None = None
    medical_transport_notes: str | None = None

    communication_notes: str | None = None
    medical_notes: str | None = None
    general_notes: str | None = None


class MobilityProfilePublic(MobilityProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
