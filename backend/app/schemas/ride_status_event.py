from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.ride_status_event import RideStatusEventType


class RideStatusEventCreate(BaseModel):
    status: RideStatusEventType
    note: Optional[str] = None


class RideStatusEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    transport_request_id: uuid.UUID
    status: RideStatusEventType
    note: Optional[str]
    created_by_user_id: Optional[uuid.UUID]
    created_at: datetime
