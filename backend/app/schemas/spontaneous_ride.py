import uuid
from typing import Annotated

from pydantic import BaseModel, Field


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
