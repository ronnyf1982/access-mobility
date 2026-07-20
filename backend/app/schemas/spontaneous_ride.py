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
    status: TransportRequestStatus
    created_at: datetime
