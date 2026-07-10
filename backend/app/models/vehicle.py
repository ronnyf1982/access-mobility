import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VehicleType(str, Enum):
    standard_car = "standard_car"
    comfort_car = "comfort_car"
    wheelchair_van = "wheelchair_van"
    wheelchair_bus = "wheelchair_bus"
    multi_passenger_van = "multi_passenger_van"
    stretcher_vehicle = "stretcher_vehicle"
    other = "other"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    license_plate: Mapped[str] = mapped_column(String(20), nullable=False)
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SAEnum(VehicleType, name="vehicletype"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Kapazität
    seat_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wheelchair_space_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    escort_seat_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Ausstattung
    has_ramp: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_lift: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_wheelchair_restraint: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_electric_wheelchair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_stretcher_transport: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_child_seat: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_low_entry: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_extra_wide_door: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Medizinische Ausstattung / Krankentransport
    has_stretcher: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_stretcher_mount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_medical_equipment_storage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_oxygen_mount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_first_aid_kit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_hygiene_equipment: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_non_emergency_medical_transport: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_transport_chair: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_infusion_mount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_two_person_crew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    patient_compartment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Maße, Gewicht & Zufahrt
    vehicle_length_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vehicle_width_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vehicle_width_with_mirrors_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    vehicle_height_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wheelbase_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    turning_circle_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    empty_weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gross_vehicle_weight_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload_capacity_kg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    requires_large_parking_space: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suitable_for_narrow_streets: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suitable_for_underground_parking: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_parking_assist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    access_restriction_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Betrieb
    home_base_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    current_location_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    general_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
