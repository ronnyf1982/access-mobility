import uuid
from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Enum as SAEnum, ForeignKey, Index, String, Text, Time, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TransportRequestStatus(str, Enum):
    draft = "draft"
    requested = "requested"
    cancelled = "cancelled"


class TransportRequest(Base):
    __tablename__ = "transport_requests"
    __table_args__ = (
        Index("ix_transport_requests_passenger_user_id", "passenger_user_id"),
        Index("ix_transport_requests_requester_user_id", "requester_user_id"),
        Index("ix_transport_requests_status", "status"),
        Index("ix_transport_requests_pickup_date", "pickup_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Wer stellt die Anfrage, für wen?
    requester_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    passenger_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)

    transport_type_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[TransportRequestStatus] = mapped_column(
        SAEnum(TransportRequestStatus, name="transportrequeststatus"),
        default=TransportRequestStatus.draft,
        nullable=False,
        server_default="draft",
    )

    # Adressen
    pickup_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    pickup_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    destination_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Zeit
    pickup_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pickup_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    arrival_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_round_trip: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    return_time_known: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    return_pickup_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    # Snapshots — bewahren Anforderungen zum Erstellzeitpunkt.
    # Verhindert, dass spätere Profiländerungen alte Anfragen fachlich verändern.
    requirement_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    mobility_profile_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Zeitstempel
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
