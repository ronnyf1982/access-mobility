from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.vehicle import VehicleType


class VehicleBase(BaseModel):
    name: str
    license_plate: str
    vehicle_type: VehicleType
    is_active: bool = True
    seat_count: int = Field(default=0, ge=0)
    wheelchair_space_count: int = Field(default=0, ge=0)
    escort_seat_count: Optional[int] = None
    has_ramp: bool = False
    has_lift: bool = False
    has_wheelchair_restraint: bool = False
    supports_electric_wheelchair: bool = False
    supports_stretcher_transport: bool = False
    has_child_seat: bool = False
    has_low_entry: bool = False
    has_extra_wide_door: bool = False
    has_stretcher: bool = False
    has_stretcher_mount: bool = False
    has_medical_equipment_storage: bool = False
    has_oxygen_mount: bool = False
    has_first_aid_kit: bool = False
    has_hygiene_equipment: bool = False
    supports_non_emergency_medical_transport: bool = False
    has_transport_chair: bool = False
    has_infusion_mount: bool = False
    supports_two_person_crew: bool = False
    patient_compartment_notes: Optional[str] = None
    vehicle_length_cm: Optional[int] = None
    vehicle_width_cm: Optional[int] = None
    vehicle_width_with_mirrors_cm: Optional[int] = None
    vehicle_height_cm: Optional[int] = None
    wheelbase_cm: Optional[int] = None
    turning_circle_m: Optional[float] = None
    empty_weight_kg: Optional[int] = None
    gross_vehicle_weight_kg: Optional[int] = None
    payload_capacity_kg: Optional[int] = None
    requires_large_parking_space: bool = False
    suitable_for_narrow_streets: bool = False
    suitable_for_underground_parking: bool = False
    has_parking_assist: bool = False
    access_restriction_notes: Optional[str] = None
    home_base_address: Optional[str] = None
    current_location_notes: Optional[str] = None
    equipment_notes: Optional[str] = None
    general_notes: Optional[str] = None


class VehicleCreate(VehicleBase):
    organization_id: uuid.UUID


class VehicleUpdate(BaseModel):
    name: Optional[str] = None
    license_plate: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    is_active: Optional[bool] = None
    seat_count: Optional[int] = Field(default=None, ge=0)
    wheelchair_space_count: Optional[int] = Field(default=None, ge=0)
    escort_seat_count: Optional[int] = None
    has_ramp: Optional[bool] = None
    has_lift: Optional[bool] = None
    has_wheelchair_restraint: Optional[bool] = None
    supports_electric_wheelchair: Optional[bool] = None
    supports_stretcher_transport: Optional[bool] = None
    has_child_seat: Optional[bool] = None
    has_low_entry: Optional[bool] = None
    has_extra_wide_door: Optional[bool] = None
    has_stretcher: Optional[bool] = None
    has_stretcher_mount: Optional[bool] = None
    has_medical_equipment_storage: Optional[bool] = None
    has_oxygen_mount: Optional[bool] = None
    has_first_aid_kit: Optional[bool] = None
    has_hygiene_equipment: Optional[bool] = None
    supports_non_emergency_medical_transport: Optional[bool] = None
    has_transport_chair: Optional[bool] = None
    has_infusion_mount: Optional[bool] = None
    supports_two_person_crew: Optional[bool] = None
    patient_compartment_notes: Optional[str] = None
    vehicle_length_cm: Optional[int] = None
    vehicle_width_cm: Optional[int] = None
    vehicle_width_with_mirrors_cm: Optional[int] = None
    vehicle_height_cm: Optional[int] = None
    wheelbase_cm: Optional[int] = None
    turning_circle_m: Optional[float] = None
    empty_weight_kg: Optional[int] = None
    gross_vehicle_weight_kg: Optional[int] = None
    payload_capacity_kg: Optional[int] = None
    requires_large_parking_space: Optional[bool] = None
    suitable_for_narrow_streets: Optional[bool] = None
    suitable_for_underground_parking: Optional[bool] = None
    has_parking_assist: Optional[bool] = None
    access_restriction_notes: Optional[str] = None
    home_base_address: Optional[str] = None
    current_location_notes: Optional[str] = None
    equipment_notes: Optional[str] = None
    general_notes: Optional[str] = None


class VehiclePublic(VehicleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
