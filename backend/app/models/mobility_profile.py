import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WheelchairType(str, Enum):
    manual = "manual"
    electric = "electric"
    unknown = "unknown"


class MobilityProfile(Base):
    __tablename__ = "mobility_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )

    # Persönliche Angaben
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date_of_birth: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Notfallkontakt
    emergency_contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Mobilitätsbedarf
    uses_wheelchair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    wheelchair_type: Mapped[WheelchairType | None] = mapped_column(
        SAEnum(WheelchairType, name="wheelchairtype"), nullable=True
    )
    uses_rollator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    uses_crutches: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blind_or_visually_impaired: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_deaf_or_hard_of_hearing: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    needs_escort: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    needs_entry_assistance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    needs_door_to_door_assistance: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    needs_ramp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    needs_lift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    needs_stretcher_transport: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Fahrzeug- / Service-Hinweise
    can_transfer_to_seat: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_own_wheelchair: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_wheelchair_space: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_extra_time: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Freitextfelder — alle freiwillig
    communication_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    medical_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    general_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
