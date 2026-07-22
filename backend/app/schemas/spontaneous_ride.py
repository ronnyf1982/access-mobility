import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.transport_request import TransportRequestStatus


class SpontaneousRideMatchRequest(BaseModel):
    pickup_latitude: Annotated[float, Field(ge=-90.0, le=90.0)]
    pickup_longitude: Annotated[float, Field(ge=-180.0, le=180.0)]
    passenger_user_id: uuid.UUID | None = None


class SpontaneousRideMatchResult(BaseModel):
    driver_id: uuid.UUID
    driver_display_name: str
    vehicle_id: uuid.UUID
    vehicle_label: str
    vehicle_type: str
    vehicle_latitude: float
    vehicle_longitude: float
    distance_km: float
    estimated_arrival_minutes: int
    matched_capabilities: list[str]
    can_accept_now: bool = True


class SpontaneousRideBookRequest(BaseModel):
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID
    pickup_latitude: Annotated[float, Field(ge=-90.0, le=90.0)]
    pickup_longitude: Annotated[float, Field(ge=-180.0, le=180.0)]
    pickup_address: str | None = None
    destination_address: str | None = None
    passenger_user_id: uuid.UUID | None = None


class SpontaneousRideBookResponse(BaseModel):
    request_id: uuid.UUID
    status: TransportRequestStatus
    driver_display_name: str
    vehicle_label: str
    estimated_arrival_minutes: int


class SpontaneousRideRequestItem(BaseModel):
    id: uuid.UUID
    passenger_user_id: uuid.UUID
    passenger_display_name: str | None = None
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: str | None = None
    destination_address: str | None = None
    status: TransportRequestStatus
    created_at: datetime


# ── Sprint 12D: Fahrer-Standort & Live-Tracking ───────────────────────────────

class DriverLocationUpdate(BaseModel):
    latitude: Annotated[float, Field(ge=-90.0, le=90.0)]
    longitude: Annotated[float, Field(ge=-180.0, le=180.0)]
    transport_request_id: uuid.UUID | None = None


class SpontaneousRideTracking(BaseModel):
    transport_request_id: uuid.UUID
    status: TransportRequestStatus
    can_track: bool
    # Nur wenn Fahrer angenommen hat und Position vorhanden — keine sensiblen Daten
    driver_id: uuid.UUID | None = None
    driver_display_name: str | None = None
    vehicle_id: uuid.UUID | None = None
    vehicle_label: str | None = None
    driver_latitude: float | None = None
    driver_longitude: float | None = None
    pickup_latitude: float | None = None
    pickup_longitude: float | None = None
    pickup_address: str | None = None
    destination_address: str | None = None
    distance_km: float | None = None
    estimated_arrival_minutes: int | None = None
    last_location_update: datetime | None = None
    ride_status_label: str
    # Sprint 12K: Auto-Rematch
    next_request_id: uuid.UUID | None = None
    request_expires_at: datetime | None = None
