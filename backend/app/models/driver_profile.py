import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DriverProfile(Base):
    __tablename__ = "driver_profiles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    default_vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vehicles.id"), nullable=True, default=None
    )

    # Qualifikationen — Grundqualifikationen
    can_assist_wheelchair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_secure_wheelchair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_operate_lift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_assist_blind_passengers: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_assist_deaf_passengers: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_handle_stretcher: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_first_aid_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_passenger_transport_license: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_support_medical_transport: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Medizinische Qualifikationen
    has_sanitaetshelfer_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_rettungshelfer_qualification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_rettungssanitaeter_qualification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_rettungsassistent_qualification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_notfallsanitaeter_qualification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_nursing_qualification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_medical_assistant_qualification: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Technische Zusatzausbildungen
    has_hygiene_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_infection_protection_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_wheelchair_restraint_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_lift_operation_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_stretcher_handling_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_transport_chair_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_oxygen_equipment_training: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Betrieb
    home_base_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    availability_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    qualification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    general_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
