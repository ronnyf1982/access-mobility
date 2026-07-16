import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.driver_shift import ShiftStatus
from app.models.vehicle import VehicleType


class VehicleBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    license_plate: str
    vehicle_type: VehicleType
    wheelchair_space_count: int
    has_ramp: bool
    has_lift: bool
    supports_stretcher_transport: bool
    supports_electric_wheelchair: bool


class DriverShiftPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    driver_profile_id: uuid.UUID
    vehicle_id: uuid.UUID
    status: ShiftStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    break_started_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DriverShiftWithVehicle(BaseModel):
    shift: DriverShiftPublic
    vehicle: VehicleBrief


class DriverShiftStartRequest(BaseModel):
    vehicle_id: Optional[uuid.UUID] = None
    license_plate: Optional[str] = None
    notes: Optional[str] = None


class DriverProfileBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    display_name: str
    default_vehicle_id: Optional[uuid.UUID] = None


class DriverDashboardContext(BaseModel):
    """Alles was die Fahrer-App beim Start braucht: Profil, Standardfahrzeug, aktive Schicht."""

    profile: DriverProfileBrief
    default_vehicle: Optional[VehicleBrief] = None
    active_shift: Optional[DriverShiftWithVehicle] = None
