import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AddressType(str, Enum):
    home = "home"
    school = "school"
    work_workshop = "work_workshop"
    daycare = "daycare"
    doctor = "doctor"
    other = "other"


class PassengerSavedAddress(Base):
    __tablename__ = "passenger_saved_addresses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mobility_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobility_profiles.id"), nullable=False
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    address_type: Mapped[AddressType] = mapped_column(
        SAEnum(AddressType, name="addresstype"), default=AddressType.other, nullable=False
    )
    street_address: Mapped[str] = mapped_column(String(500), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    city: Mapped[str] = mapped_column(String(200), nullable=False)
    additional_info: Mapped[str | None] = mapped_column(String(500), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_default_pickup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_default_destination: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
