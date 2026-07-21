import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContactType(str, Enum):
    emergency_contact = "emergency_contact"
    trusted_person = "trusted_person"
    caregiver = "caregiver"
    school = "school"
    workshop = "workshop"
    daycare = "daycare"
    doctor = "doctor"
    nursing_service = "nursing_service"
    parent = "parent"
    other = "other"


class PassengerContact(Base):
    __tablename__ = "passenger_contacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    mobility_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("mobility_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role_label: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_type: Mapped[ContactType] = mapped_column(
        SAEnum(ContactType, name="contacttype"),
        default=ContactType.other,
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_emergency_contact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visible_to_driver: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    visible_in_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    callable_in_emergency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    priority: Mapped[int] = mapped_column(Integer, default=999, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
