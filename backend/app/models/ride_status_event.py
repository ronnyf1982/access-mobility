import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RideStatusEventType(str, Enum):
    driver_on_way = "driver_on_way"
    driver_arrived = "driver_arrived"
    passenger_picked_up = "passenger_picked_up"
    ride_started = "ride_started"
    ride_completed = "ride_completed"
    ride_cancelled = "ride_cancelled"
    issue_reported = "issue_reported"


class RideStatusEvent(Base):
    __tablename__ = "ride_status_events"
    __table_args__ = (
        Index("ix_ride_status_events_transport_request_id", "transport_request_id"),
        Index("ix_ride_status_events_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    transport_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("transport_requests.id"), nullable=False
    )
    status: Mapped[RideStatusEventType] = mapped_column(
        SAEnum(RideStatusEventType, name="ridestatuseventtype"), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
