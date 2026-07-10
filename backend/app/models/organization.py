import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrganizationType(str, Enum):
    employer = "employer"
    school = "school"
    facility = "facility"
    medical_practice = "medical_practice"
    insurer = "insurer"
    transport_provider = "transport_provider"
    other = "other"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[OrganizationType] = mapped_column(
        SAEnum(OrganizationType, name="organizationtype"), nullable=False
    )
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Adresse
    address_line: Mapped[str | None] = mapped_column(String(500), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True, default="DE")

    # Fahrdienst-spezifisch (für type=transport_provider)
    dispatch_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    dispatch_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operating_area_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
