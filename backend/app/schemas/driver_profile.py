from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class DriverProfileBase(BaseModel):
    display_name: str
    phone: Optional[str] = None
    is_active: bool = True
    can_assist_wheelchair: bool = False
    can_secure_wheelchair: bool = False
    can_operate_lift: bool = False
    can_assist_blind_passengers: bool = False
    can_assist_deaf_passengers: bool = False
    can_handle_stretcher: bool = False
    has_first_aid_training: bool = False
    has_passenger_transport_license: bool = False
    can_support_medical_transport: bool = False
    has_sanitaetshelfer_training: bool = False
    has_rettungshelfer_qualification: bool = False
    has_rettungssanitaeter_qualification: bool = False
    has_rettungsassistent_qualification: bool = False
    has_notfallsanitaeter_qualification: bool = False
    has_nursing_qualification: bool = False
    has_medical_assistant_qualification: bool = False
    has_hygiene_training: bool = False
    has_infection_protection_training: bool = False
    has_wheelchair_restraint_training: bool = False
    has_lift_operation_training: bool = False
    has_stretcher_handling_training: bool = False
    has_transport_chair_training: bool = False
    has_oxygen_equipment_training: bool = False
    home_base_address: Optional[str] = None
    availability_notes: Optional[str] = None
    qualification_notes: Optional[str] = None
    general_notes: Optional[str] = None


class DriverProfileCreate(DriverProfileBase):
    user_id: uuid.UUID
    organization_id: uuid.UUID


class DriverProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    can_assist_wheelchair: Optional[bool] = None
    can_secure_wheelchair: Optional[bool] = None
    can_operate_lift: Optional[bool] = None
    can_assist_blind_passengers: Optional[bool] = None
    can_assist_deaf_passengers: Optional[bool] = None
    can_handle_stretcher: Optional[bool] = None
    has_first_aid_training: Optional[bool] = None
    has_passenger_transport_license: Optional[bool] = None
    can_support_medical_transport: Optional[bool] = None
    has_sanitaetshelfer_training: Optional[bool] = None
    has_rettungshelfer_qualification: Optional[bool] = None
    has_rettungssanitaeter_qualification: Optional[bool] = None
    has_rettungsassistent_qualification: Optional[bool] = None
    has_notfallsanitaeter_qualification: Optional[bool] = None
    has_nursing_qualification: Optional[bool] = None
    has_medical_assistant_qualification: Optional[bool] = None
    has_hygiene_training: Optional[bool] = None
    has_infection_protection_training: Optional[bool] = None
    has_wheelchair_restraint_training: Optional[bool] = None
    has_lift_operation_training: Optional[bool] = None
    has_stretcher_handling_training: Optional[bool] = None
    has_transport_chair_training: Optional[bool] = None
    has_oxygen_equipment_training: Optional[bool] = None
    home_base_address: Optional[str] = None
    availability_notes: Optional[str] = None
    qualification_notes: Optional[str] = None
    general_notes: Optional[str] = None


class DriverProfilePublic(DriverProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
