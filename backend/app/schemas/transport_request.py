from __future__ import annotations

import uuid
from datetime import date, datetime, time
from enum import Enum as PyEnum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.transport_request import TransportRequestStatus


class TransportRequestCreate(BaseModel):
    passenger_user_id: Optional[uuid.UUID] = None
    organization_id: Optional[uuid.UUID] = None
    transport_type_id: Optional[str] = None
    status: TransportRequestStatus = TransportRequestStatus.draft
    pickup_address: Optional[str] = None
    pickup_details: Optional[str] = None
    destination_address: Optional[str] = None
    destination_details: Optional[str] = None
    pickup_date: Optional[date] = None
    pickup_time: Optional[time] = None
    arrival_time: Optional[time] = None
    is_round_trip: bool = False
    return_time_known: bool = False
    return_pickup_time: Optional[time] = None
    requirement_snapshot: Optional[dict[str, Any]] = None
    mobility_profile_snapshot: Optional[dict[str, Any]] = None
    notes: Optional[str] = None


class TransportRequestUpdate(BaseModel):
    transport_type_id: Optional[str] = None
    pickup_address: Optional[str] = None
    pickup_details: Optional[str] = None
    destination_address: Optional[str] = None
    destination_details: Optional[str] = None
    pickup_date: Optional[date] = None
    pickup_time: Optional[time] = None
    arrival_time: Optional[time] = None
    is_round_trip: Optional[bool] = None
    return_time_known: Optional[bool] = None
    return_pickup_time: Optional[time] = None
    requirement_snapshot: Optional[dict[str, Any]] = None
    mobility_profile_snapshot: Optional[dict[str, Any]] = None
    notes: Optional[str] = None


class TransportRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requester_user_id: uuid.UUID
    passenger_user_id: uuid.UUID
    organization_id: Optional[uuid.UUID]
    transport_type_id: Optional[str]
    status: TransportRequestStatus
    pickup_address: Optional[str]
    pickup_details: Optional[str]
    destination_address: Optional[str]
    destination_details: Optional[str]
    pickup_date: Optional[date]
    pickup_time: Optional[time]
    arrival_time: Optional[time]
    is_round_trip: bool
    return_time_known: bool
    return_pickup_time: Optional[time]
    requirement_snapshot: Optional[dict[str, Any]]
    mobility_profile_snapshot: Optional[dict[str, Any]]
    notes: Optional[str]
    # Disposition
    assigned_vehicle_id: Optional[uuid.UUID]
    assigned_driver_profile_id: Optional[uuid.UUID]
    assigned_by_user_id: Optional[uuid.UUID]
    assigned_at: Optional[datetime]
    assignment_notes: Optional[str]
    # Timestamps
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    # Fahrgast-Kontaktdaten (für Dispo-Rollen sichtbar, sonst None)
    passenger_display_name: Optional[str] = None
    passenger_email: Optional[str] = None
    passenger_phone: Optional[str] = None
    passenger_emergency_contact_name: Optional[str] = None
    passenger_emergency_contact_phone: Optional[str] = None


class TransportRequestListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    requester_user_id: uuid.UUID
    passenger_user_id: uuid.UUID
    transport_type_id: Optional[str]
    status: TransportRequestStatus
    pickup_address: Optional[str]
    destination_address: Optional[str]
    pickup_date: Optional[date]
    pickup_time: Optional[time]
    is_round_trip: bool
    assigned_vehicle_id: Optional[uuid.UUID]
    assigned_driver_profile_id: Optional[uuid.UUID]
    assigned_at: Optional[datetime]
    assignment_notes: Optional[str]
    created_at: datetime
    submitted_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    # Fahrgast-Kontaktdaten (für Dispo-Rollen)
    passenger_display_name: Optional[str] = None
    passenger_email: Optional[str] = None
    passenger_phone: Optional[str] = None


# ── Matching ─────────────────────────────────────────────────────────────────


class MatchStatus(str, PyEnum):
    suitable = "suitable"
    warning = "warning"
    unsuitable = "unsuitable"


class MatchingVehicleOption(BaseModel):
    vehicle_id: uuid.UUID
    name: str
    license_plate: str
    vehicle_type: str
    status: MatchStatus
    reasons: list[str]
    missing_requirements: list[str]
    matched_requirements: list[str]


class MatchingDriverOption(BaseModel):
    driver_profile_id: uuid.UUID
    display_name: str
    status: MatchStatus
    reasons: list[str]
    missing_requirements: list[str]
    matched_requirements: list[str]


class MatchingOptionsResponse(BaseModel):
    request_id: uuid.UUID
    vehicles: list[MatchingVehicleOption]
    drivers: list[MatchingDriverOption]


class TransportRequestAssign(BaseModel):
    vehicle_id: uuid.UUID
    driver_profile_id: uuid.UUID
    assignment_notes: Optional[str] = None
