from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.models.transport_request import TransportRequestStatus


class TransportRequestCreate(BaseModel):
    passenger_user_id: Optional[uuid.UUID] = None  # None → wird zu requester_user_id
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
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    cancelled_at: Optional[datetime]


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
    created_at: datetime
    submitted_at: Optional[datetime]
    cancelled_at: Optional[datetime]
